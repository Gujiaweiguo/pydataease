#!/usr/bin/env bash
# chmod +x install.sh
# PyDataEase 安装脚本
# 用法: ./install.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载函数库
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/checks.sh"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/docker.sh"

# ========== 主流程 ==========

log_info "=========================================="
log_info "  PyDataEase 安装程序"
log_info "=========================================="

# 1. 加载环境变量
load_env

# 2. 验证必需配置
log_info "验证安装配置..."

if [[ -z "${DE_SECRET_KEY:-}" ]]; then
    die "缺少必需配置: DE_SECRET_KEY。请在 conf/install.env 中设置。"
fi
if [[ -z "${DE_SHARE_SECRET_KEY:-}" ]]; then
    die "缺少必需配置: DE_SHARE_SECRET_KEY。请在 conf/install.env 中设置。"
fi
if [[ -z "${DE_ADMIN_PASSWORD:-}" ]]; then
    die "缺少必需配置: DE_ADMIN_PASSWORD。请在 conf/install.env 中设置。"
fi

# 3. 检查密钥不能相同
if [[ "${DE_SECRET_KEY}" == "${DE_SHARE_SECRET_KEY}" ]]; then
    log_warn "DE_SECRET_KEY 与 DE_SHARE_SECRET_KEY 相同，建议使用不同的密钥以提高安全性"
fi

log_info "配置验证通过 ✓"

# 4. 系统环境检查
run_all_checks

# 5. 权限检查
ensure_root_or_docker

# 6. 创建目录结构
INSTALL_DIR="$(get_install_dir)"
log_info "创建安装目录: ${INSTALL_DIR}"

mkdir -p "${INSTALL_DIR}/data/postgres"
mkdir -p "${INSTALL_DIR}/data/backups"
mkdir -p "${INSTALL_DIR}/logs/app"
mkdir -p "${INSTALL_DIR}/logs/scripts"
mkdir -p "${INSTALL_DIR}/static"
mkdir -p "${INSTALL_DIR}/conf/nginx"
mkdir -p "${INSTALL_DIR}/release"
mkdir -p "${INSTALL_DIR}/bin"

log_info "目录结构创建完成 ✓"

# 7. 复制管理脚本到安装目录（如果从其他位置运行）
if [[ "${SCRIPT_DIR}" != "${INSTALL_DIR}/bin" ]]; then
    log_info "复制管理脚本到 ${INSTALL_DIR}/bin/ ..."
    cp -f "${SCRIPT_DIR}/install.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -f "${SCRIPT_DIR}/start.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -f "${SCRIPT_DIR}/stop.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -f "${SCRIPT_DIR}/upgrade.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -f "${SCRIPT_DIR}/uninstall.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -f "${SCRIPT_DIR}/status.sh" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    cp -rf "${SCRIPT_DIR}/lib" "${INSTALL_DIR}/bin/" 2>/dev/null || true
    log_info "脚本复制完成 ✓"
fi

# 8. 加载离线镜像（如果配置了）
load_images

# 9. 生成 docker-compose.yml
log_info "生成 docker-compose.yml..."

# 查找模板文件：优先从脚本同级 conf/ 目录查找
COMPOSE_TEMPLATE=""
if [[ -f "${SCRIPT_DIR}/conf/docker-compose.yml.template" ]]; then
    COMPOSE_TEMPLATE="${SCRIPT_DIR}/conf/docker-compose.yml.template"
elif [[ -f "${INSTALL_DIR}/conf/docker-compose.yml.template" ]]; then
    COMPOSE_TEMPLATE="${INSTALL_DIR}/conf/docker-compose.yml.template"
else
    die "未找到 docker-compose.yml.template 模板文件"
fi

# 使用 envsubst 替换环境变量
mkdir -p "${INSTALL_DIR}/conf"
envsubst < "${COMPOSE_TEMPLATE}" > "${INSTALL_DIR}/conf/docker-compose.yml"
log_info "docker-compose.yml 生成完成 ✓"

# 10. 验证生成的 compose 文件
log_info "验证 docker-compose.yml 配置..."
docker compose -f "${INSTALL_DIR}/conf/docker-compose.yml" config --quiet
log_info "docker-compose.yml 验证通过 ✓"

# 11. 根据数据库模式启动
DE_PG_MODE="${DE_PG_MODE:-builtin}"

if [[ "${DE_PG_MODE}" == "builtin" ]]; then
    # 内置模式：先启动 PostgreSQL
    log_info "启动内置 PostgreSQL 数据库..."
    compose_cmd up -d pydataease-pg

    # 等待 PostgreSQL 就绪
    log_info "等待 PostgreSQL 就绪..."
    pg_ready=false
    for i in $(seq 1 30); do
        if compose_cmd exec -T pydataease-pg pg_isready -U dataease &>/dev/null; then
            pg_ready=true
            break
        fi
        sleep 2
    done
    if [[ "${pg_ready}" != true ]]; then
        die "PostgreSQL 启动超时，请检查日志"
    fi
    log_info "PostgreSQL 已就绪 ✓"
elif [[ "${DE_PG_MODE}" == "external" ]]; then
    # 外部模式：验证数据库连通性
    log_info "使用外部 PostgreSQL 数据库..."
    pg_host="${DE_DATABASE_HOST:-${DE_DATABASE_URL:-}}"
    if [[ -z "${pg_host}" ]]; then
        die "外部 PostgreSQL 模式需要设置 DE_DATABASE_HOST 或 DE_DATABASE_URL"
    fi
    log_info "外部数据库配置: ${pg_host}"
    log_warn "请确保外部数据库已创建并可访问"
else
    die "不支持的 DE_PG_MODE 值: ${DE_PG_MODE}（支持 builtin 或 external）"
fi

# 12. 运行数据库迁移
log_info "运行数据库迁移 (Alembic)..."
run_oneoff alembic upgrade head
log_info "数据库迁移完成 ✓"

# 13. 初始化管理员账户
log_info "初始化管理员账户..."
DE_ADMIN_PASSWORD="${DE_ADMIN_PASSWORD}" run_oneoff python -m app.commands.init_admin
log_info "管理员账户初始化完成 ✓"

# 14. 启动所有服务
compose_up

# 15. 等待健康检查
wait_for_health

# 16. 写入版本信息
DE_VERSION="${DE_VERSION:-dev}"
echo "${DE_VERSION}" > "${INSTALL_DIR}/release/VERSION"
log_info "版本信息已写入: ${DE_VERSION}"

# 17. 打印安装成功信息
DE_PORT="${DE_PORT:-8100}"
log_info "=========================================="
log_info "  PyDataEase 安装成功！"
log_info "=========================================="
echo ""
log_info "访问地址: http://<服务器IP>:${DE_PORT}"
log_info "管理员账号: admin"
log_info "安装目录: ${INSTALL_DIR}"
echo ""
log_info "管理命令:"
echo "  启动: ${INSTALL_DIR}/bin/start.sh"
echo "  停止: ${INSTALL_DIR}/bin/stop.sh"
echo "  状态: ${INSTALL_DIR}/bin/status.sh"
echo "  升级: ${INSTALL_DIR}/bin/upgrade.sh"
echo "  卸载: ${INSTALL_DIR}/bin/uninstall.sh"
