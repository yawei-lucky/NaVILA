#!/usr/bin/env python3
"""Minimal G1 motion executor (step-1 practical implementation).

Design goal:
- Reuse existing command dispatch stack (holosoma / Unitree wrapper)
- Offer stable primitives: forward / turn / stop
- Enforce e-stop and command-timeout safety

This file is dependency-light so you can run it locally before wiring real robot APIs.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol


class Action(str, Enum):
    FORWARD = "forward"
    TURN = "turn"
    STOP = "stop"


@dataclass
class MidLevelCommand:
    action: Action
    value: float = 0.0
    duration_s: float = 0.0


class VelocityDispatcher(Protocol):
    """Adapter protocol for existing dispatch stack.

    Implement this over your current sender (holosoma / unitree sdk wrapper).
    """

    def send_velocity(self, vx: float, wz: float) -> None:
        ...

    def stop(self) -> None:
        ...


class ExecutorState(str, Enum):
    IDLE = "IDLE"
    EXECUTING = "EXECUTING"
    STOPPING = "STOPPING"
    ESTOP = "ESTOP"


class MotionExecutor:
    def __init__(
        self,
        dispatcher: VelocityDispatcher,
        timeout_ms: int = 200,
        max_vx: float = 0.4,
        max_wz: float = 0.8,
    ) -> None:
        self.dispatcher = dispatcher
        self.timeout_s = timeout_ms / 1000.0
        self.max_vx = abs(max_vx)
        self.max_wz = abs(max_wz)

        self.state = ExecutorState.IDLE
        self.last_cmd_ts: Optional[float] = None
        self.exec_until_ts: Optional[float] = None
        self.e_stop_enabled = False

    def apply(self, cmd: MidLevelCommand) -> None:
        now = time.monotonic()
        self.last_cmd_ts = now

        if self.e_stop_enabled:
            self._enter_estop("command_rejected_estop")
            return

        # clamp and sanitize
        if cmd.action == Action.FORWARD:
            vx = max(-self.max_vx, min(self.max_vx, cmd.value))
            self.dispatcher.send_velocity(vx=vx, wz=0.0)
            self.exec_until_ts = now + max(0.0, cmd.duration_s)
            self.state = ExecutorState.EXECUTING
            self._log(f"FORWARD vx={vx:.3f} duration={cmd.duration_s:.3f}s")
            return

        if cmd.action == Action.TURN:
            wz = max(-self.max_wz, min(self.max_wz, cmd.value))
            self.dispatcher.send_velocity(vx=0.0, wz=wz)
            self.exec_until_ts = now + max(0.0, cmd.duration_s)
            self.state = ExecutorState.EXECUTING
            self._log(f"TURN wz={wz:.3f} duration={cmd.duration_s:.3f}s")
            return

        self._enter_stop("normal")

    def set_estop(self, enabled: bool) -> None:
        self.e_stop_enabled = enabled
        if enabled:
            self._enter_estop("manual_estop")
        else:
            self.state = ExecutorState.IDLE
            self._log("E-STOP released")

    def tick(self) -> None:
        now = time.monotonic()

        if self.e_stop_enabled:
            return

        # Duration completion has higher priority than timeout when both are true.
        if self.state == ExecutorState.EXECUTING and self.exec_until_ts is not None:
            if now >= self.exec_until_ts:
                self._enter_stop("duration_done")
                return

        if self.state == ExecutorState.EXECUTING and self.last_cmd_ts is not None:
            if now - self.last_cmd_ts > self.timeout_s:
                self._enter_stop("timeout")
                return

    def _enter_stop(self, reason: str) -> None:
        self.state = ExecutorState.STOPPING
        self.dispatcher.stop()
        self._log(f"STOP reason={reason}")
        self.state = ExecutorState.IDLE

    def _enter_estop(self, reason: str) -> None:
        self.state = ExecutorState.ESTOP
        self.dispatcher.stop()
        self._log(f"ESTOP reason={reason}")

    def _log(self, msg: str) -> None:
        ts = int(time.time() * 1000)
        print(f"[{ts}] state={self.state.value} {msg}")


class MockDispatcher:
    """Reference dispatcher used for local validation.

    Replace this with your real adapter over holosoma / Unitree SDK wrapper.
    """

    def send_velocity(self, vx: float, wz: float) -> None:
        print(f"dispatch velocity -> vx={vx:.3f}, wz={wz:.3f}")

    def stop(self) -> None:
        print("dispatch STOP")


def run_demo(timeout_ms: int) -> None:
    ex = MotionExecutor(dispatcher=MockDispatcher(), timeout_ms=timeout_ms)

    ex.apply(MidLevelCommand(Action.FORWARD, value=0.25, duration_s=0.3))
    time.sleep(0.1)
    ex.tick()

    ex.apply(MidLevelCommand(Action.TURN, value=0.5, duration_s=0.2))
    time.sleep(0.25)
    ex.tick()  # duration done

    ex.apply(MidLevelCommand(Action.FORWARD, value=0.1, duration_s=1.0))
    time.sleep((timeout_ms + 50) / 1000.0)
    ex.tick()  # timeout

    ex.set_estop(True)
    ex.apply(MidLevelCommand(Action.FORWARD, value=0.2, duration_s=0.5))
    ex.set_estop(False)
    ex.apply(MidLevelCommand(Action.STOP))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal G1 motion executor")
    parser.add_argument("--timeout-ms", type=int, default=200)
    parser.add_argument("--demo", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        run_demo(timeout_ms=args.timeout_ms)
        return

    print("Run with --demo for built-in flow validation.")


if __name__ == "__main__":
    main()
