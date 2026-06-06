#!/usr/bin/env bash
# chmod +x start.sh
# PyDataEase 启动脚本
# 用法: ./start.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"

# ========== 主流程 ==========

log_info "=========================================="
log_info "  PyDataEase 启动"
log_info "=========================================="

# 1. 加载环境变量
load_env

# 2. 检查是否已安装
INSTALL_DIR="$(get_install_dir)"
VERSION_FILE="${INSTALL_DIR}/release/VERSION"

if [[ ! -f "${VERSION_FILE}" ]]; then
    die "PyDataEase 尚未安装。请先运行 ./install.sh"
fi

CURRENT_VERSION=$(cat "${VERSION_FILE}")
log_info "当前版本: ${CURRENT_VERSION}"

# 3. 启动服务
compose_up

# 4. 等待健康检查
wait_for_health

# 5. 打印访问信息
DE_PORT="${DE_PORT:-8100}"
log_info "=========================================="
log_info "  PyDataEase 已启动"
log_info "=========================================="
echo ""
log_info "访问地址: http://<服务器IP>:${DE_PORT}"
log_info "查看状态: ${SCRIPT_DIR}/status.sh"
log_info "查看日志: docker compose -f ${INSTALL_DIR}/conf/docker-compose.yml logs -f"
