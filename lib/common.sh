#!/usr/bin/env bash
# chmod +x lib/common.sh
# 公共函数库 - 日志、环境变量、基础检查
set -euo pipefail

# 颜色定义
readonly _RED='\033[0;31m'
readonly _GREEN='\033[0;32m'
readonly _YELLOW='\033[0;33m'
readonly _NC='\033[0m' # No Color

# 获取当前脚本所在目录（lib/）
COMMON_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly COMMON_LIB_DIR

# 日志脚本目录（如果存在则同时写入文件）
_log_dir() {
    local install_dir
    install_dir="$(get_install_dir 2>/dev/null || echo "/opt/module/pydataease")"
    echo "${install_dir}/logs/scripts"
}

# 带时间戳的日志输出
_log() {
    local level="$1"
    shift
    local color="$1"
    shift
    local msg
    msg="$(date '+%Y-%m-%d %H:%M:%S') [${level}] $*"
    echo -e "${color}${msg}${_NC}"
    # 如果日志目录存在，同时写入文件
    local log_dir
    log_dir="$(_log_dir)"
    if [[ -d "${log_dir}" ]]; then
        echo "${msg}" >> "${log_dir}/$(date '+%Y-%m-%d').log"
    fi
}

log_info()  { _log "INFO"  "${_GREEN}"  "$@"; }
log_warn()  { _log "WARN"  "${_YELLOW}" "$@"; }
log_error() { _log "ERROR" "${_RED}"    "$@"; }

# 输出错误信息并退出
die() {
    log_error "$@"
    exit 1
}

# 加载环境变量配置文件
# 优先从 DE_INSTALL_DIR/conf/install.env 加载，否则从脚本同级 conf/ 加载
load_env() {
    local env_file=""

    # 优先查找安装目录下的配置
    if [[ -n "${DE_INSTALL_DIR:-}" && -f "${DE_INSTALL_DIR}/conf/install.env" ]]; then
        env_file="${DE_INSTALL_DIR}/conf/install.env"
    elif [[ -f "${COMMON_LIB_DIR}/../conf/install.env" ]]; then
        env_file="${COMMON_LIB_DIR}/../conf/install.env"
    fi

    if [[ -n "${env_file}" ]]; then
        log_info "加载配置文件: ${env_file}"
        # 导出所有变量
        set -a
        # shellcheck disable=SC1090
        source "${env_file}"
        set +a
    else
        log_warn "未找到配置文件 conf/install.env，将使用环境变量或默认值"
    fi
}

# 检查当前用户是否有权限运行 docker
ensure_root_or_docker() {
    if [[ "$(id -u)" -eq 0 ]]; then
        return 0
    fi
    if groups | grep -q '\bdocker\b'; then
        return 0
    fi
    die "当前用户无 Docker 权限。请使用 root 用户或将当前用户加入 docker 组。"
}

# 获取安装目录
get_install_dir() {
    echo "${DE_INSTALL_DIR:-/opt/module/pydataease}"
}
