#!/usr/bin/env bash
# chmod +x uninstall.sh
# PyDataEase 卸载脚本
# 用法: ./uninstall.sh [--force] [--purge]
#   --force  跳过确认提示
#   --purge  删除所有数据（包括数据库、配置、日志）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"

# ========== 解析参数 ==========

FORCE=false
PURGE=false

for arg in "$@"; do
    case "${arg}" in
        --force)  FORCE=true ;;
        --purge)  PURGE=true ;;
        *)        log_warn "未知参数: ${arg}" ;;
    esac
done

# ========== 主流程 ==========

log_info "=========================================="
log_info "  PyDataEase 卸载"
log_info "=========================================="

# 1. 加载环境变量
load_env

INSTALL_DIR="$(get_install_dir)"

# 2. 确认提示（除非 --force）
if [[ "${FORCE}" != true ]]; then
    log_warn "即将卸载 PyDataEase (安装目录: ${INSTALL_DIR})"
    if [[ "${PURGE}" == true ]]; then
        log_warn "⚠ --purge 模式：将删除所有数据（包括数据库、配置、日志）！"
    else
        log_info "将保留数据和配置文件（使用 --purge 可完全删除）"
    fi
    echo ""
    read -rp "确认卸载？(yes/no): " confirm
    if [[ "${confirm}" != "yes" ]]; then
        log_info "卸载已取消"
        exit 0
    fi
fi

# 3. 停止并删除容器
log_info "停止并删除容器..."
compose_down || {
    log_warn "停止容器时出现异常，继续卸载..."
}

# 4. 清理操作
if [[ "${PURGE}" == true ]]; then
    # 完全删除模式
    log_info "删除安装目录: ${INSTALL_DIR}..."

    # 删除 Docker 镜像
    log_info "清理 Docker 镜像..."
    DE_IMAGE="${DE_IMAGE:-pydataease/pydataease-app:latest}"
    docker rmi "${DE_IMAGE}" 2>/dev/null || {
        log_warn "删除应用镜像失败（可能不存在或被其他容器使用）"
    }

    DE_PG_IMAGE="${DE_PG_IMAGE:-pgvector/pgvector:pg16}"
    docker rmi "${DE_PG_IMAGE}" 2>/dev/null || {
        log_warn "删除 PG 镜像失败（可能不存在或被其他容器使用）"
    }

    DE_NGINX_IMAGE="${DE_NGINX_IMAGE:-nginx:stable}"
    docker rmi "${DE_NGINX_IMAGE}" 2>/dev/null || {
        log_warn "删除 Nginx 镜像失败（可能不存在或被其他容器使用）"
    }

    # 删除安装目录
    if [[ -d "${INSTALL_DIR}" ]]; then
        rm -rf "${INSTALL_DIR}"
        log_info "安装目录已删除 ✓"
    fi
else
    # 保留数据模式：仅删除容器相关文件
    log_info "保留数据和配置文件..."

    # 删除 compose 文件（容器编排配置）
    COMPOSE_FILE="${INSTALL_DIR}/conf/docker-compose.yml"
    if [[ -f "${COMPOSE_FILE}" ]]; then
        rm -f "${COMPOSE_FILE}"
        log_info "已删除 docker-compose.yml"
    fi

    # 删除版本文件
    VERSION_FILE="${INSTALL_DIR}/release/VERSION"
    if [[ -f "${VERSION_FILE}" ]]; then
        rm -f "${VERSION_FILE}"
        log_info "已删除版本文件"
    fi
fi

# 5. 打印卸载确认
log_info "=========================================="
log_info "  PyDataEase 已卸载"
log_info "=========================================="
echo ""
if [[ "${PURGE}" == true ]]; then
    log_info "所有数据已清除"
else
    log_info "数据和配置文件保留在: ${INSTALL_DIR}"
    log_info "如需完全删除，请运行: rm -rf ${INSTALL_DIR}"
fi
