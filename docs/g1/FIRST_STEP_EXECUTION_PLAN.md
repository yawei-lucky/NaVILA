# 第一步落地计划（代码级）：复用现有指令下达封装，先跑通 forward / turn / stop

> 目标：不重写底层，直接对接你已有的 holosoma / Unitree 指令下发模块，
> 在代码层先得到可验证的最小执行器。

## 1. 你现在就做这三件事

1) 把你现有“发速度命令”的封装抽象成两个函数：
- `send_velocity(vx, wz)`
- `stop()`

2) 用 `scripts/g1_executor/motion_executor.py` 作为执行器核心：
- 输入中层命令：`forward(value, duration)` / `turn(value, duration)` / `stop()`
- 自动处理：限幅、duration 到点停机、超时停机、急停。

3) 先跑本地 demo，再替换成真机 dispatcher：
```bash
python scripts/g1_executor/motion_executor.py --demo --timeout-ms 200
```

## 2. 文件说明

- `scripts/g1_executor/motion_executor.py`
  - `VelocityDispatcher`：适配你已有封装的协议层（关键）
  - `MotionExecutor`：状态机与安全逻辑
  - `MockDispatcher`：本地验证使用

## 3. 如何接你的现有封装（最小改动）

你只需新建一个 adapter 类，满足 `VelocityDispatcher` 协议：

```python
class HoloSomaDispatcher:
    def __init__(self, holo_client):
        self.client = holo_client

    def send_velocity(self, vx: float, wz: float) -> None:
        self.client.send_velocity(vx=vx, wz=wz)

    def stop(self) -> None:
        self.client.send_velocity(vx=0.0, wz=0.0)
```

然后替换：

```python
executor = MotionExecutor(dispatcher=HoloSomaDispatcher(holo_client), timeout_ms=200)
```

## 4. 第一阶段验收标准（代码级）

必须满足：
- forward 到时自动停；
- turn 到时自动停；
- 超时（默认 200ms）自动停；
- e-stop 打开后所有运动命令拒绝并保持 stop；
- 所有状态都有日志（IDLE/EXECUTING/STOPPING/ESTOP）。

## 5. 下一步（你确认第一步通过后再做）

- 把执行器挂到 ROS2 topic（`/navila_mid_cmd`）
- 再把上层视觉理解输出映射成 `MidLevelCommand`
