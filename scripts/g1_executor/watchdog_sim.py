#!/usr/bin/env python3
"""A minimal watchdog simulator for G1 motion executor phase-1 bring-up.

This script does not require ROS2. It validates the timeout + e-stop behavior first.

Usage:
  python scripts/g1_executor/watchdog_sim.py --timeout-ms 200 --demo
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExecutorState(str, Enum):
    IDLE = "IDLE"
    EXECUTING = "EXECUTING"
    STOPPING = "STOPPING"


@dataclass
class MidCommand:
    action: str
    value: float = 0.0
    duration_s: float = 0.0


class SafetyWatchdog:
    def __init__(self, timeout_ms: int = 200) -> None:
        self.timeout_s = timeout_ms / 1000.0
        self.state = ExecutorState.IDLE
        self.last_cmd_ts: Optional[float] = None
        self.e_stop = False

    def on_command(self, cmd: MidCommand) -> None:
        now = time.monotonic()
        self.last_cmd_ts = now

        if self.e_stop:
            self._enter_stop("manual_e_stop")
            return

        if cmd.action not in {"forward", "turn", "stop"}:
            self._enter_stop("invalid_action")
            return

        if cmd.action == "stop":
            self._enter_stop("normal")
            return

        self.state = ExecutorState.EXECUTING
        self._log(f"execute action={cmd.action} value={cmd.value:.3f} duration={cmd.duration_s:.3f}s")

    def on_e_stop(self, enabled: bool = True) -> None:
        self.e_stop = enabled
        if enabled:
            self._enter_stop("manual_e_stop")
        else:
            self.state = ExecutorState.IDLE
            self._log("e_stop released -> IDLE")

    def tick(self) -> None:
        if self.e_stop:
            return

        if self.state == ExecutorState.EXECUTING and self.last_cmd_ts is not None:
            delta = time.monotonic() - self.last_cmd_ts
            if delta > self.timeout_s:
                self._enter_stop("timeout")

    def _enter_stop(self, reason: str) -> None:
        self.state = ExecutorState.STOPPING
        self._log(f"STOP reason={reason}")
        self.state = ExecutorState.IDLE

    def _log(self, message: str) -> None:
        ts = int(time.time() * 1000)
        print(f"[{ts}] state={self.state.value} {message}")


def run_demo(timeout_ms: int) -> None:
    wd = SafetyWatchdog(timeout_ms=timeout_ms)
    wd.on_command(MidCommand("forward", value=0.2, duration_s=1.0))
    time.sleep((timeout_ms + 50) / 1000.0)
    wd.tick()  # should timeout stop

    wd.on_command(MidCommand("turn", value=0.5, duration_s=0.8))
    wd.on_e_stop(True)  # immediate stop

    wd.on_e_stop(False)
    wd.on_command(MidCommand("stop"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safety watchdog simulator for G1 executor phase-1")
    parser.add_argument("--timeout-ms", type=int, default=200, help="command timeout in milliseconds")
    parser.add_argument("--demo", action="store_true", help="run built-in demo sequence")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        run_demo(args.timeout_ms)
        return

    print("Interactive mode. Inputs: forward <v> <sec> | turn <w> <sec> | stop | estop_on | estop_off | tick | quit")
    wd = SafetyWatchdog(timeout_ms=args.timeout_ms)

    while True:
        raw = input("> ").strip()
        if not raw:
            continue

        if raw == "quit":
            break
        if raw == "tick":
            wd.tick()
            continue
        if raw == "estop_on":
            wd.on_e_stop(True)
            continue
        if raw == "estop_off":
            wd.on_e_stop(False)
            continue
        if raw == "stop":
            wd.on_command(MidCommand("stop"))
            continue

        parts = raw.split()
        if len(parts) != 3 or parts[0] not in {"forward", "turn"}:
            print("Invalid input")
            continue

        action, value, duration = parts
        wd.on_command(MidCommand(action, value=float(value), duration_s=float(duration)))


if __name__ == "__main__":
    main()
