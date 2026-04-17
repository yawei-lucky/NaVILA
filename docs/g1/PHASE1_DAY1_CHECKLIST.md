# G1 落地第一项（Day 1）执行清单：联通与安全底座

> 目标：先把“能停下来”做好，再做“能走起来”。

## 1) 先确认计划文件位置

当前仓库中的总计划文件在：

- `G1_MIN_EXECUTOR_PLAN.md`（仓库根目录）

常用查找命令：

```bash
# 在仓库根目录执行
find . -maxdepth 2 -name 'G1_MIN_EXECUTOR_PLAN.md'

# 或者搜索所有 G1 相关文档
find . -maxdepth 3 -path './.git' -prune -o -iname '*g1*' -type f -print
```

## 2) Day 1 必做项（可打勾）

- [ ] 网络联通：控制机能 ping 到 G1。
- [ ] DDS/ROS2 域配置确认（Domain ID 一致）。
- [ ] 能获取机器人状态（至少一条心跳/状态消息）。
- [ ] 能下发 `stop`（空速度）控制。
- [ ] 急停可触发（手动）。
- [ ] 命令超时自动停机可触发（自动，推荐 200ms）。

## 3) 建议的“先停后动”验收顺序

1. **只测 stop**：连续发 10 次 stop，确保每次都停。
2. **测超时停机**：发送一次 forward 后停止发命令，确认超时自动 stop。
3. **测急停**：运动中触发急停，确认立刻进入 stop 状态。

## 4) 最小日志字段（今天就加）

建议每条日志至少包含：

- 时间戳（ms）
- 命令 ID
- action（forward/turn/stop）
- value, duration
- 当前状态（IDLE/EXECUTING/STOPPING）
- stop 原因（manual_e_stop / timeout / normal）

## 5) 今日产出（Day 1 Definition of Done）

满足以下条件即算 Day 1 完成：

- 能稳定执行 `stop`。
- 超时无命令会自动进入 `stop`。
- 能触发手动急停并在日志中看到原因。
- 形成可复现的最小测试脚本（本仓库先用 `scripts/g1_executor/watchdog_sim.py` 验证逻辑）。
