# G1 Executor Scripts (Phase-1)

## 目的
用于在接入 ROS2/Unitree SDK 前，先验证最关键的安全逻辑：

- 命令超时自动 `stop`
- 手动急停 `e_stop`
- `forward / turn / stop` 的最小状态机行为

## 快速开始

```bash
python scripts/g1_executor/watchdog_sim.py --timeout-ms 200 --demo
```

如果进入交互模式：

```bash
python scripts/g1_executor/watchdog_sim.py
# 示例输入
forward 0.2 1.0
tick
estop_on
estop_off
stop
quit
```

> 说明：这是逻辑模拟器，不直接控制 G1 硬件。
