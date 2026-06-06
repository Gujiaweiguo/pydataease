#!/usr/bin/env bash
# chmod +x stop.sh
# PyDataEase 停止脚本
# 用法: ./stop.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"

# ========== 主流程 ==========

log_info "=========================================="
log_info "  PyDataEase 停止"
log_info "=========================================="

# 1. 加载环境变量
load_env

# 2. 停止服务
compose_stop

# 3. 打印确认信息
DE_PORT="${DE_PORT:-8100}"
log_info "=========================================="
log_info "  PyDataEase 已停止"
log_info "=========================================="
echo ""
log_info "服务已在端口 ${DE_PORT} 上停止"
log_info "重新启动: ${SCRIPT_DIR}/start.sh"
