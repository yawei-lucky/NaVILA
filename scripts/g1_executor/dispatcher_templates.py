#!/usr/bin/env python3
"""Dispatcher templates for integrating MotionExecutor with existing command stacks.

This file intentionally avoids importing vendor SDKs so it can be copied into
real robot projects with minimal edits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class VelocityLikeClient(Protocol):
    def send_velocity(self, vx: float, wz: float) -> None:
        ...


@dataclass
class HoloSomaDispatcher:
    """Adapter for a holosoma-side client exposing send_velocity(vx, wz)."""

    client: VelocityLikeClient

    def send_velocity(self, vx: float, wz: float) -> None:
        self.client.send_velocity(vx=vx, wz=wz)

    def stop(self) -> None:
        self.client.send_velocity(vx=0.0, wz=0.0)


@dataclass
class SDK2Dispatcher:
    """Adapter for a Unitree SDK2-like client exposing move(vx, vy, vyaw)."""

    client: object

    def send_velocity(self, vx: float, wz: float) -> None:
        # Replace with your SDK call, for example:
        # self.client.Move(vx, 0.0, wz)
        move = getattr(self.client, "Move")
        move(vx, 0.0, wz)

    def stop(self) -> None:
        move = getattr(self.client, "Move")
        move(0.0, 0.0, 0.0)


if __name__ == "__main__":
    print("Use HoloSomaDispatcher or SDK2Dispatcher in motion_executor integration.")
