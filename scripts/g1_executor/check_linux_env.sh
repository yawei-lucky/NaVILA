#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <G1_IP>"
  exit 1
fi

G1_IP="$1"

echo "[1/5] OS info"
uname -a || true
if command -v lsb_release >/dev/null 2>&1; then
  lsb_release -a || true
fi

echo

echo "[2/5] Network interfaces"
if command -v ip >/dev/null 2>&1; then
  ip -br a || true
else
  echo "ip command not found (install iproute2)"
fi

echo

echo "[3/5] Ping G1"
ping -c 4 "$G1_IP"

echo

echo "[4/5] ROS2 availability"
if command -v ros2 >/dev/null 2>&1; then
  echo "ros2 found: $(command -v ros2)"
  ros2 --help >/dev/null 2>&1 && echo "ros2 command works"
else
  echo "ros2 not found"
fi

echo

echo "[5/5] DDS env"
echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-<unset>}"
echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-<unset>}"
echo "CYCLONEDDS_URI=${CYCLONEDDS_URI:-<unset>}"

echo

echo "Done. If ping failed, fix networking before ROS2/SDK validation."
