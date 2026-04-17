# 第一阶段最终方案（从 0 起步，先稳）：SDK2 Python 主线 + 可替换 Holosoma 后端

> 目标：一周内稳定跑通 `forward / turn / stop + watchdog + e-stop + camera input`。

## 为什么这样定（最终结论）

- **第一主线用 `unitree_sdk2_python`**：官方示例覆盖速度控制、状态读取与相机，最适合 0→1 起步。
- **Holosoma 作为可替换 locomotion backend**：当你已有链路时直接接入 adapter，不阻塞第一周。
- **LeRobot/Psi0 不作为第一周阻塞项**：它们适合后续扩展视觉理解、数据采集与复杂策略。

## 第一阶段范围（只做 6 件事）

1. 连接 G1 并稳定读取状态（心跳/姿态/模式）。
2. 能发送速度命令（vx, wz）。
3. 跑通 `forward(duration)`。
4. 跑通 `turn(duration)`。
5. 跑通 `stop()` 与 timeout 自动停机。
6. 接前置相机并完成“看见目标->停下”的最小闭环触发。

> 不做：抓取、复杂路径规划、端到端 VLA。

## 代码结构（当前仓库可直接使用）

- 执行器核心：`scripts/g1_executor/motion_executor.py`
- 接入计划：`docs/g1/FIRST_STEP_EXECUTION_PLAN.md`
- 本阶段最终验收：本文件

## 你需要实现的唯一对接点

实现 `VelocityDispatcher` 两个函数（其余逻辑复用执行器）：

- `send_velocity(vx, wz)`
- `stop()`

可选来源：
- `SDK2Dispatcher`（推荐第一周）
- `HoloSomaDispatcher`（如果你师弟链路已通）

## 每日任务（5天）

### Day 1：通信+安全
- 跑通状态读取。
- `stop()` 连续 20 次成功。
- timeout（200ms）触发自动停机。

### Day 2：forward / turn
- 速度限幅：`|vx|<=0.3`, `|wz|<=0.6`。
- `forward 1.0s`、`turn 1.0s` 可重复执行。

### Day 3：稳定性
- 连续 30 组命令序列（forward->turn->stop）无失控。
- 强制 e-stop 测试通过。

### Day 4：相机接入
- 接前置相机流。
- 先做规则触发：识别到目标框面积阈值后 stop。

### Day 5：最小 demo
- Demo 定义：**“看见目标 -> 走近 -> 停稳”**。
- 记录日志和失败样本，形成下一阶段输入。

## 本阶段 DoD（完成定义）

必须全部满足：
- 运动命令可控、可停、可复现。
- 任意异常（断链/非法命令）能进入 stop。
- 相机触发 stop 的闭环可重复演示。

## 第二阶段再做什么（先不做）

- 上层理解（VLM）接入中层命令。
- 双臂动作叠加（arm overlay / teleop 数据）。
- 再评估 LeRobot/Psi0 的训练与部署链路。
