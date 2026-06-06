#!/usr/bin/env bash
# chmod +x upgrade.sh
# PyDataEase 升级脚本
# 用法: ./upgrade.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/checks.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/backup.sh"

# ========== 主流程 ==========

log_info "=========================================="
log_info "  PyDataEase 升级"
log_info "=========================================="

# 1. 加载环境变量
load_env

# 2. 升级前检查
run_upgrade_checks

INSTALL_DIR="$(get_install_dir)"
DE_PG_MODE="${DE_PG_MODE:-builtin}"
DE_VERSION="${DE_VERSION:-dev}"

# 3. 读取当前版本
VERSION_FILE="${INSTALL_DIR}/release/VERSION"
if [[ ! -f "${VERSION_FILE}" ]]; then
    die "未找到版本信息 (${VERSION_FILE})。请确认已正确安装。"
fi
CURRENT_VERSION=$(cat "${VERSION_FILE}")
log_info "当前版本: ${CURRENT_VERSION}"
log_info "目标版本: ${DE_VERSION}"

if [[ "${CURRENT_VERSION}" == "${DE_VERSION}" ]]; then
    log_warn "目标版本与当前版本相同 (${DE_VERSION})，继续执行升级..."
fi

# 4. 数据库备份
BACKUP_FILE=""
if [[ "${DE_PG_MODE}" == "builtin" ]]; then
    log_info "内置数据库模式：自动备份数据库..."
    BACKUP_FILE=$(backup_database)
    log_info "备份文件: ${BACKUP_FILE}"
else
    # 外部数据库：提示用户手动备份
    log_warn "=========================================="
    log_warn "  使用外部 PostgreSQL 数据库"
    log_warn "  请确保已手动备份数据库！"
    log_warn "=========================================="
    echo ""
    read -rp "已完成数据库备份？(yes/no): " confirm_backup
    if [[ "${confirm_backup}" != "yes" ]]; then
        die "升级已取消。请先备份数据库后再执行升级。"
    fi
fi

# 5. 加载新版本镜像
load_images

# 6. 停止应用和 Nginx 容器（保持 PG 运行）
log_info "停止应用和 Nginx 容器..."
compose_cmd stop pydataease-app pydataease-nginx 2>/dev/null || {
    log_warn "停止容器时出现异常，继续升级..."
}

# 7. 运行数据库迁移
log_info "运行数据库迁移 (Alembic)..."
MIGRATION_OK=false
if run_oneoff alembic upgrade head; then
    MIGRATION_OK=true
    log_info "数据库迁移完成 ✓"
else
    log_error "数据库迁移失败！"
    MIGRATION_OK=false
fi

# 8. 迁移失败回滚
if [[ "${MIGRATION_OK}" != true ]]; then
    if [[ "${DE_PG_MODE}" == "builtin" && -n "${BACKUP_FILE}" ]]; then
        log_error "正在回滚数据库..."
        restore_database "${BACKUP_FILE}"

        log_info "重新启动旧版本容器..."
        compose_up
        die "数据库迁移失败，已回滚到旧版本。请检查日志后重试。"
    else
        die "数据库迁移失败且无法自动回滚（外部数据库模式）。请手动恢复数据库。"
    fi
fi

# 9. 启动新版本容器
log_info "启动新版本服务..."
compose_up

# 10. 等待健康检查
HEALTH_OK=false
if wait_for_health; then
    HEALTH_OK=true
else
    HEALTH_OK=false
fi

# 11. 健康检查失败处理
if [[ "${HEALTH_OK}" != true ]]; then
    log_error "=========================================="
    log_error "  健康检查失败！"
    log_error "=========================================="
    log_error "服务可能未正常启动，请手动检查："
    echo ""
    echo "  1. 查看容器日志:"
    echo "     docker compose -f ${INSTALL_DIR}/conf/docker-compose.yml logs"
    echo ""
    echo "  2. 查看容器状态:"
    echo "     docker compose -f ${INSTALL_DIR}/conf/docker-compose.yml ps"
    echo ""
    if [[ -n "${BACKUP_FILE}" ]]; then
        echo "  3. 如需回滚，备份文件位于:"
        echo "     ${BACKUP_FILE}"
    fi
    die "升级过程中健康检查失败，请手动排查"
fi

# 12. 更新版本信息
echo "${DE_VERSION}" > "${VERSION_FILE}"
log_info "版本已更新: ${CURRENT_VERSION} → ${DE_VERSION}"

# 13. 打印升级成功信息
DE_PORT="${DE_PORT:-8100}"
log_info "=========================================="
log_info "  PyDataEase 升级成功！"
log_info "=========================================="
echo ""
log_info "版本: ${CURRENT_VERSION} → ${DE_VERSION}"
log_info "访问地址: http://<服务器IP>:${DE_PORT}"
if [[ -n "${BACKUP_FILE}" ]]; then
    log_info "备份文件: ${BACKUP_FILE}"
fi
