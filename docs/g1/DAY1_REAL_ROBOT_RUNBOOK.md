# Day-1 实机联通 Runbook（G1 最小运动执行器）

> 你问的核心是：要不要先找 Linux 电脑连真机、先验证能不能通？
>
> 答案：**是的**。`watchdog_sim.py` 只是本地安全逻辑演示，Day-1 的下一步就是“Linux 控制机 ↔ G1 真机”联通验证。

---

## 0) 先明确两件事

1. `python scripts/g1_executor/watchdog_sim.py --timeout-ms 200 --demo`
   - 作用：验证你写的“超时停机/急停状态机逻辑”没问题。
   - 局限：**不连接真机**，不验证网络、DDS、ROS2、SDK。

2. Day-1 实机目标
   - 一台 Linux 控制机能和 G1 通信。
   - 能看到状态流（至少一个稳定状态源）。
   - 能发送 `stop` 类命令并确认机器人停住。

---

## 1) 你现在需要的硬件/环境

- 一台 Linux 电脑（建议 Ubuntu 20.04/22.04）。
- 与 G1 同网段连接（网线直连或同交换机）。
- 安装基础工具：`python3`, `iproute2`, `ping`, `ssh`。
- 若走 ROS2：安装 ROS2 + CycloneDDS；若走 SDK：安装 Unitree SDK2。

> 先不要同时上 ROS2+SDK 两套链路。先选一条最短路径打通。

---

## 2) 推荐执行顺序（从低风险到高风险）

### Step A：本地安全逻辑先通过（你已开始）

```bash
python scripts/g1_executor/watchdog_sim.py --timeout-ms 200 --demo
```

期望看到 `STOP reason=timeout` 和 `STOP reason=manual_e_stop`。

### Step B：Linux 与真机网络联通

```bash
# 查看本机网卡与 IP
ip -br a

# 把 <G1_IP> 换成你机器人控制网口 IP
ping -c 4 <G1_IP>
```

通过标准：丢包率低且 RTT 稳定。

### Step C：通信中间件可见性验证（ROS2 或 SDK 二选一）

#### 方案 C1：ROS2 路线

```bash
# 先统一 DDS 实现（CycloneDDS）
echo $RMW_IMPLEMENTATION

# source ROS2 环境
source /opt/ros/<distro>/setup.bash

# 查看是否能发现话题（联通后应该有数据变化）
ros2 topic list
```

#### 方案 C2：SDK 路线

- 运行 SDK 自带最小 demo，先只读状态，不发运动命令。
- 确认状态流频率稳定后，再进入 stop 命令验证。

### Step D：仅验证 stop（不要先 forward）

- 先发 10 轮 stop。
- 每轮确认：控制返回成功 + 机器人保持稳定停止。
- 任意异常立即急停并回到 Step B/C 排查。

---

## 3) 一次标准 Day-1 验证记录（建议）

至少记录：
- 测试时间、场地、操作者。
- Linux 主机 IP / G1 IP / 使用链路（ROS2 or SDK）。
- 状态读取是否连续。
- stop 连续 10 次结果。
- 急停是否可用。
- 结论：是否进入 Day-2（执行器节点接线）。

---

## 4) 常见问题速查

1. **ping 不通**
   - 多数是网段不一致、网线/交换机问题、防火墙拦截。
2. **能 ping 通但看不到 ROS2 话题**
   - 常见是 DDS Domain ID 不一致，或 RMW 实现不一致。
3. **能读状态但控制不稳定**
   - 先只发 stop，降低控制频率，检查命令重复发送策略。

---

## 5) 你下一条可以直接给我的信息

为了我帮你进入 Day-2，请直接发这 6 项：

1. Linux 版本（`lsb_release -a`）
2. 是否已装 ROS2（发行版）
3. G1 IP（可脱敏）
4. `ping -c 4 <G1_IP>` 结果
5. `ros2 topic list`（若走 ROS2）
6. 你当前想走 ROS2 还是 SDK2
