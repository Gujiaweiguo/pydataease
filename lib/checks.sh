#!/usr/bin/env bash
# chmod +x lib/checks.sh
# 系统环境检查函数库
set -euo pipefail

CHECKS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${CHECKS_LIB_DIR}/common.sh"

# 版本号比较辅助函数：返回 0 表示 $1 >= $2
_version_gte() {
    local ver1="$1" ver2="$2"
    # 将版本号转为可比较的整数序列
    local IFS=.
    local -a arr1=(${ver1}) arr2=(${ver2})
    local i len1=${#arr1[@]} len2=${#arr2[@]}
    local max_len=$(( len1 > len2 ? len1 : len2 ))
    for ((i = 0; i < max_len; i++)); do
        local v1="${arr1[i]:-0}"
        local v2="${arr2[i]:-0}"
        if (( v1 > v2 )); then
            return 0
        elif (( v1 < v2 )); then
            return 1
        fi
    done
    return 0
}

# 检查操作系统 - 仅警告，不阻断
check_os() {
    log_info "检查操作系统..."
    if [[ ! -f /etc/os-release ]]; then
        log_warn "无法检测操作系统 (/etc/os-release 不存在)"
        return 0
    fi
    # shellcheck disable=SC1091
    source /etc/os-release
    local os_name="${ID:-unknown}"
    local os_version="${VERSION_ID:-0}"

    if [[ "${os_name}" != "ubuntu" ]]; then
        log_warn "当前操作系统为 ${PRETTY_NAME:-${os_name} ${os_version}}，建议使用 Ubuntu 22.04+"
        return 0
    fi

    if _version_gte "${os_version}" "22.04"; then
        log_info "操作系统: Ubuntu ${os_version} ✓"
    else
        log_warn "Ubuntu 版本 ${os_version} 低于建议的 22.04，可能存在兼容性问题"
    fi
}

# 检查 Docker Engine 版本 >= 24.0 - 阻断性检查
check_docker() {
    log_info "检查 Docker Engine..."
    if ! command -v docker &>/dev/null; then
        die "未找到 Docker。请先安装 Docker Engine >= 24.0。"
    fi

    local docker_version
    docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null) || {
        die "无法获取 Docker 版本。请确认 Docker 服务是否正在运行。"
    }

    if _version_gte "${docker_version}" "24.0"; then
        log_info "Docker Engine ${docker_version} ✓"
    else
        die "Docker Engine 版本 ${docker_version} 低于要求的 24.0。请升级 Docker。"
    fi
}

# 检查 Docker Compose V2 - 阻断性检查
check_compose_v2() {
    log_info "检查 Docker Compose V2..."
    if docker compose version &>/dev/null; then
        local compose_ver
        compose_ver=$(docker compose version --short 2>/dev/null || echo "unknown")
        log_info "Docker Compose ${compose_ver} ✓"
    else
        die "未找到 Docker Compose V2 (docker compose)。请安装 Compose 插件。"
    fi
}

# 检查磁盘空间 >= 10GB - 阻断性检查
check_disk() {
    log_info "检查磁盘空间..."
    local install_dir
    install_dir="$(get_install_dir)"
    # 确保目录或其父目录存在
    local check_dir="${install_dir}"
    while [[ ! -d "${check_dir}" ]]; do
        check_dir="$(dirname "${check_dir}")"
    done

    local avail_kb
    avail_kb=$(df -P "${check_dir}" | awk 'NR==2 {print $4}')
    local avail_gb=$(( avail_kb / 1024 / 1024 ))

    if (( avail_gb >= 10 )); then
        log_info "可用磁盘空间: ${avail_gb}GB ✓"
    else
        die "可用磁盘空间仅 ${avail_gb}GB，需要至少 10GB。请清理磁盘或更换安装目录。"
    fi
}

# 检查内存大小 - 仅警告，不阻断
check_memory() {
    log_info "检查内存..."
    if [[ ! -f /proc/meminfo ]]; then
        log_warn "无法检测内存大小 (/proc/meminfo 不存在)"
        return 0
    fi

    local mem_total_kb
    mem_total_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_total_gb=$(( mem_total_kb / 1024 / 1024 ))

    if (( mem_total_gb >= 4 )); then
        log_info "系统内存: ${mem_total_gb}GB ✓"
    else
        log_warn "系统内存仅 ${mem_total_gb}GB，建议至少 4GB 以保证运行稳定"
    fi
}

# 检查端口是否被占用 - 阻断性检查
check_port() {
    local port="${DE_PORT:-8100}"
    log_info "检查端口 ${port}..."
    if ss -tlnp 2>/dev/null | grep -q ":${port} "; then
        local occupant
        occupant=$(ss -tlnp 2>/dev/null | grep ":${port} " | head -1 || echo "未知")
        die "端口 ${port} 已被占用: ${occupant}"
    fi
    log_info "端口 ${port} 可用 ✓"
}

# 检查安装目录的父目录 - 阻断性检查
check_install_dir() {
    local install_dir
    install_dir="$(get_install_dir)"
    log_info "检查安装目录: ${install_dir}"

    local parent_dir
    parent_dir="$(dirname "${install_dir}")"

    if [[ ! -d "${parent_dir}" ]]; then
        die "安装目录的父目录 ${parent_dir} 不存在"
    fi
    if [[ ! -w "${parent_dir}" ]]; then
        die "安装目录的父目录 ${parent_dir} 不可写。请检查权限。"
    fi
    log_info "安装目录检查通过 ✓"
}

# 运行全部安装前检查
run_all_checks() {
    log_info "========== 开始系统环境检查 =========="
    check_os
    check_docker
    check_compose_v2
    check_disk
    check_memory
    check_port
    check_install_dir
    log_info "========== 系统环境检查全部通过 =========="
}

# 运行升级前检查（子集）
run_upgrade_checks() {
    log_info "========== 开始升级前检查 =========="
    check_docker
    check_compose_v2
    check_disk
    check_install_dir
    log_info "========== 升级前检查全部通过 =========="
}

# 检查外部 PostgreSQL 连通性 - 阻断性检查
check_external_pg() {
    local pg_host="${DE_DATABASE_HOST:-}"
    local pg_port="${DE_DATABASE_PORT:-5432}"
    local pg_name="${DE_DATABASE_NAME:-dataease}"
    local pg_user="${DE_DATABASE_USER:-}"
    local pg_pass="${DE_DATABASE_PASSWORD:-}"

    log_info "检查外部 PostgreSQL 连通性..."

    if [[ -z "${pg_host}" ]]; then
        die "DE_DATABASE_HOST 未配置（external 模式必填）"
    fi

    # TCP 连通性测试
    if ! timeout 5 bash -c "echo > /dev/tcp/${pg_host}/${pg_port}" 2>/dev/null; then
        die "无法连接到 ${pg_host}:${pg_port}，请检查网络和 PostgreSQL 是否运行"
    fi
    log_info "TCP 连通 ${pg_host}:${pg_port} ✓"

    # 使用 psql 或 Python 验证登录
    if command -v psql &>/dev/null; then
        local pg_version
        pg_version=$(PGPASSWORD="${pg_pass}" psql -h "${pg_host}" -p "${pg_port}" -U "${pg_user}" -d "${pg_name}" -t -c "SELECT version();" 2>&1) || {
            die "PostgreSQL 登录失败 (${pg_host}:${pg_port}/${pg_name})，请检查用户名和密码: ${pg_version}"
        }
        log_info "PostgreSQL 登录成功 ✓"

        # 版本检查 >= 14
        local major_version
        major_version=$(echo "${pg_version}" | grep -oP 'PostgreSQL \K[0-9]+' | head -1)
        if [[ -n "${major_version}" ]] && (( major_version < 14 )); then
            die "PostgreSQL 版本 ${major_version} 低于要求的 14。当前: ${pg_version}"
        fi
        log_info "PostgreSQL 版本 ${major_version} ✓"
    else
        log_warn "psql 未安装，跳过登录验证和版本检查。建议安装 postgresql-client。"
    fi
}

# 在外部 PG 上初始化数据库和扩展（仅 DE_PG_ALLOW_INIT=true 时调用）
init_external_pg() {
    local pg_host="${DE_DATABASE_HOST:-}"
    local pg_port="${DE_DATABASE_PORT:-5432}"
    local pg_name="${DE_DATABASE_NAME:-dataease}"
    local pg_user="${DE_DATABASE_USER:-}"
    local pg_pass="${DE_DATABASE_PASSWORD:-}"

    if [[ "${DE_PG_ALLOW_INIT:-false}" != "true" ]]; then
        log_info "DE_PG_ALLOW_INIT=false，跳过外部 PG 初始化"
        return 0
    fi

    log_info "尝试在外部 PostgreSQL 上初始化..."

    if ! command -v psql &>/dev/null; then
        die "DE_PG_ALLOW_INIT=true 但 psql 未安装。请安装 postgresql-client 或手动创建数据库。"
    fi

    # 创建数据库（如不存在）
    PGPASSWORD="${pg_pass}" psql -h "${pg_host}" -p "${pg_port}" -U "${pg_user}" -d postgres \
        -c "SELECT 'CREATE DATABASE ${pg_name}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${pg_name}')\\gexec" 2>/dev/null || \
        log_warn "创建数据库失败（可能已存在或权限不足）"
    log_info "数据库 ${pg_name} 检查完成 ✓"

    # 创建 vector 扩展（如不存在）
    PGPASSWORD="${pg_pass}" psql -h "${pg_host}" -p "${pg_port}" -U "${pg_user}" -d "${pg_name}" \
        -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || \
        log_warn "创建 vector 扩展失败（可能需要超级用户权限）"
    log_info "vector 扩展检查完成 ✓"
}
