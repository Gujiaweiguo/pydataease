#!/usr/bin/env bash
# chmod +x status.sh
# PyDataEase 状态查询脚本
# 用法: ./status.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"

# ========== 主流程 ==========

load_env

INSTALL_DIR="$(get_install_dir)"
DE_PORT="${DE_PORT:-8100}"

echo "=========================================="
echo "  PyDataEase 服务状态"
echo "=========================================="
echo ""

# 1. 安装版本
echo "--- 版本信息 ---"
VERSION_FILE="${INSTALL_DIR}/release/VERSION"
if [[ -f "${VERSION_FILE}" ]]; then
    echo "  已安装版本: $(cat "${VERSION_FILE}")"
else
    echo "  未检测到版本信息（可能未安装）"
fi
echo "  安装目录:   ${INSTALL_DIR}"
echo ""

# 2. 容器状态
echo "--- 容器状态 ---"
CONTAINERS=("pydataease-nginx" "pydataease-app" "pydataease-pg")
for container in "${CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
        status=$(docker inspect --format '{{.State.Status}}' "${container}" 2>/dev/null || echo "unknown")
        case "${status}" in
            running)
                echo "  ${container}: ✓ 运行中"
                ;;
            stopped|exited)
                echo "  ${container}: ✗ 已停止"
                ;;
            paused)
                echo "  ${container}: ⏸ 已暂停"
                ;;
            *)
                echo "  ${container}: ? ${status}"
                ;;
        esac
    else
        echo "  ${container}: - 未创建"
    fi
done
echo ""

# 3. 健康检查
echo "--- 健康检查 ---"
HEALTH_URL="http://localhost:${DE_PORT}/de2api/health"
if curl -sf -o /dev/null --connect-timeout 5 "${HEALTH_URL}" 2>/dev/null; then
    health_response=$(curl -sf --connect-timeout 5 "${HEALTH_URL}" 2>/dev/null || echo "unknown")
    echo "  API 健康检查: ✓ 正常"
    echo "  响应: ${health_response}"
else
    echo "  API 健康检查: ✗ 无法连接 (${HEALTH_URL})"
fi
echo ""

# 4. 端口监听
echo "--- 端口状态 ---"
if ss -tlnp 2>/dev/null | grep -q ":${DE_PORT} "; then
    listener=$(ss -tlnp 2>/dev/null | grep ":${DE_PORT} " | head -1 || echo "")
    echo "  端口 ${DE_PORT}: ✓ 已监听"
    echo "  ${listener}"
else
    echo "  端口 ${DE_PORT}: ✗ 未监听"
fi
echo ""

# 5. 磁盘使用
echo "--- 磁盘使用 ---"
if [[ -d "${INSTALL_DIR}" ]]; then
    usage=$(du -sh "${INSTALL_DIR}" 2>/dev/null | awk '{print $1}' || echo "unknown")
    echo "  安装目录: ${usage}"
    avail=$(df -h "${INSTALL_DIR}" | awk 'NR==2 {print $4}')
    echo "  可用空间: ${avail}"
else
    echo "  安装目录不存在"
fi
echo ""

echo "=========================================="
