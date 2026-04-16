# G1 最小运动执行器下一步计划（forward / turn / stop）

## 0. 目标与验收标准（先对齐）

**唯一目标**：在 Unitree G1 上稳定执行 `forward / turn / stop` 三类命令，并具备基本安全保护。

**验收标准（必须全部满足）**：
1. 支持命令输入：`forward(vx, duration)`、`turn(wz, duration)`、`stop()`。
2. 命令发布与机器人状态回读链路可用（ROS2/SDK 通信连续 30 分钟无中断）。
3. 具备急停（手动）与命令超时自动停机（自动）。
4. 在固定测试场景下连续执行 20 组命令序列，无跌倒、无失控。
5. 形成可复用接口（为后续 NaVILA adapter 保留）。

---

## 1. 系统边界（本阶段只做什么）

### 1.1 本阶段包含
- G1 控制链路打通：控制命令下发 + 状态读取。
- 最小执行器节点：命令解析、状态机、安全守护。
- 基础动作标定：前进速度、转向角速度与执行时长映射。

### 1.2 本阶段不包含
- 不接入 NaVILA 推理。
- 不复现论文 low-level locomotion 真机策略。
- 不做复杂导航（避障/建图/全局路径规划）。

---

## 2. 建议架构（先稳定、后扩展）

```text
[cmd source: keyboard / test script]
            |
            v
   /navila_mid_cmd (自定义中层命令)
            |
            v
  g1_motion_executor (本阶段核心)
    |- command validator
    |- finite state machine
    |- safety watchdog
    |- unitree command adapter
            |
            v
     Unitree ROS2 / SDK2
            |
            v
            G1

并行：
G1 state --> /g1/state --> executor feedback & logger
```

### 2.1 推荐 ROS2 接口（先定义，后实现）
- 输入话题：`/navila_mid_cmd`
- 输出控制：`/g1/cmd_vel`（或 Unitree 对应控制话题）
- 状态订阅：`/g1/state`
- 急停输入：`/g1/e_stop`（bool）

### 2.2 中层命令消息（建议字段）
```yaml
string action        # forward | turn | stop
float32 value        # forward: m/s; turn: rad/s; stop: 0
float32 duration_s   # 执行时长，stop 可忽略
builtin_interfaces/Time stamp
string frame_id      # 预留（例如 body）
```

> 后续 NaVILA 只需要输出该结构，不需改底层执行器。

---

## 3. 两周落地计划（Day 1 ~ Day 14）

## Day 1-2：联通与安全底座
- [ ] 确认 G1 与控制机网络、DDS 域与 ROS2 发现机制。
- [ ] 跑通官方最小控制示例（单步站立/停机命令）。
- [ ] 实现手动急停通道（物理+软件二选一至少一条可用）。
- [ ] 实现 command timeout（>200ms 无新命令 -> 自动 stop）。

**里程碑 M1**：可安全发送 stop 并确认机器人可靠停机。

## Day 3-5：最小执行器节点
- [ ] 新建 `g1_motion_executor`（Python/C++ 任一，建议先 Python 快速验证）。
- [ ] 实现命令校验器（速度上限、时长上限、非法 action 拒绝）。
- [ ] 实现 FSM：`IDLE -> EXECUTING -> STOPPING -> IDLE`。
- [ ] 支持三种命令：forward / turn / stop。
- [ ] 增加执行日志（输入命令、下发控制、状态反馈、异常）。

**里程碑 M2**：命令行可稳定触发 forward / turn / stop。

## Day 6-8：参数标定与稳定性
- [ ] 标定前进速度区间（例如 0.1~0.4 m/s）。
- [ ] 标定转向角速度区间（例如 0.2~0.8 rad/s）。
- [ ] 标定 duration 与位移/转角近似关系（短时线性区间）。
- [ ] 引入加减速斜坡（避免速度阶跃）。

**里程碑 M3**：动作平顺、无明显抖动或过冲。

## Day 9-11：组合命令与回归测试
- [ ] 实现脚本化序列执行：`forward 1.0s -> turn 1.2s -> stop`。
- [ ] 完成 20 组回归（含边界值与随机组合）。
- [ ] 记录失败样本并修复（重点看 timeout 与状态切换）。

**里程碑 M4**：20 组命令序列通过率 >= 95%。

## Day 12-14：接口冻结（为接 NaVILA 做准备）
- [ ] 固化中层命令接口（字段、单位、约束、错误码）。
- [ ] 形成 `adapter contract` 文档（输入/输出/异常处理）。
- [ ] 输出一份 demo：外部仅发 3 个动作命令即可驱动 G1。

**里程碑 M5**：完成“最小运动执行器 v1.0”并可对接上层动作生成器。

---

## 4. 风险清单与应对

1. **通信抖动/丢包**：
   - 应对：watchdog + timeout stop；关键命令重复发送窗口。
2. **速度设定过激导致不稳**：
   - 应对：硬限幅 + 梯形速度曲线 + 小步增量标定。
3. **状态不可观测导致难排障**：
   - 应对：强制结构化日志（时间戳、命令ID、反馈状态）。
4. **后续对接 NaVILA 需重构**：
   - 应对：提前冻结中层命令 schema，执行器只认 schema 不认上层来源。

---

## 5. 最小实现清单（可直接开工）

- [ ] `msg/NavilaMidCmd.msg`（或等价 JSON/Proto，ROS2 推荐 msg）
- [ ] `node/g1_motion_executor.py`
- [ ] `node/g1_safety_watchdog.py`
- [ ] `scripts/send_test_cmd.py`
- [ ] `configs/limits.yaml`（速度、角速度、超时阈值）
- [ ] `README_G1_executor.md`（启动、测试、急停说明）

---

## 6. 每日站会模板（建议）

- 昨日完成：
- 今日计划：
- 阻塞问题：
- 安全项检查：急停是否可用？timeout stop 是否触发正常？
- 是否仍对齐目标：**只做 forward / turn / stop 的稳定执行**

---

## 7. 结束定义（DoD）

满足以下条件才算完成本任务：
- 三类命令可重复执行，且运动稳定。
- 任意异常（断链/异常命令）都能进入 stop。
- 具备一键测试脚本和基础运行文档。
- 上层系统可通过统一接口调用，不依赖控制细节。

> 完成以上 DoD 后，再进入下一步：把 NaVILA 输出映射到该中层接口。
