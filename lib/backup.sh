#!/usr/bin/env bash
# chmod +x lib/backup.sh
# 数据库备份与恢复函数库
set -euo pipefail

BACKUP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${BACKUP_LIB_DIR}/common.sh"
# shellcheck disable=SC1091
source "${BACKUP_LIB_DIR}/docker.sh"

# 备份目录路径
_backup_dir() {
    local install_dir
    install_dir="$(get_install_dir)"
    echo "${install_dir}/data/backups"
}

# 创建内置 PostgreSQL 数据库备份
# 返回备份文件路径
backup_database() {
    local backup_dir
    backup_dir="$(_backup_dir)"

    log_info "创建数据库备份..."
    mkdir -p "${backup_dir}"

    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${backup_dir}/${timestamp}.sql.gz"

    # 通过 docker compose 执行 pg_dump 并压缩
    compose_cmd exec -T pydataease-pg pg_dump -U dataease dataease | gzip > "${backup_file}"

    local file_size
    file_size=$(du -h "${backup_file}" | awk '{print $1}')
    log_info "数据库备份完成: ${backup_file} (${file_size})"

    echo "${backup_file}"
}

# 从备份文件恢复数据库
# 用法: restore_database <备份文件路径>
restore_database() {
    local backup_file="$1"

    if [[ ! -f "${backup_file}" ]]; then
        die "备份文件不存在: ${backup_file}"
    fi

    log_info "从备份恢复数据库: ${backup_file}"

    # 解压并通过管道导入
    gunzip -c "${backup_file}" | compose_cmd exec -T pydataease-pg psql -U dataease dataease

    log_info "数据库恢复完成 ✓"
}

# 列出所有备份文件（按日期排序）
list_backups() {
    local backup_dir
    backup_dir="$(_backup_dir)"

    if [[ ! -d "${backup_dir}" ]]; then
        log_warn "备份目录不存在: ${backup_dir}"
        return 0
    fi

    local files
    files=$(find "${backup_dir}" -name '*.sql.gz' -type f 2>/dev/null | sort)
    if [[ -z "${files}" ]]; then
        log_warn "未找到任何备份文件"
        return 0
    fi

    log_info "现有备份文件:"
    while IFS= read -r f; do
        local file_size
        file_size=$(du -h "${f}" | awk '{print $1}')
        echo "  $(basename "${f}") (${file_size})"
    done <<< "${files}"
}

# 获取最新备份文件路径
get_latest_backup() {
    local backup_dir
    backup_dir="$(_backup_dir)"

    if [[ ! -d "${backup_dir}" ]]; then
        echo ""
        return 1
    fi

    local latest
    latest=$(find "${backup_dir}" -name '*.sql.gz' -type f 2>/dev/null | sort | tail -1)
    if [[ -z "${latest}" ]]; then
        echo ""
        return 1
    fi

    echo "${latest}"
}
