#!/usr/bin/env bash
set -euo pipefail

# =============================================
# PyDataEase 构建发布脚本
# 在构建服务器上运行，产出自包含的离线安装包
#
# 用法:
#   ./build-release.sh                    # 自动读取版本号
#   ./build-release.sh -v 2.10            # 指定版本号
#   ./build-release.sh -v 2.10 -o /tmp    # 指定输出目录
# =============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认值
VERSION=""
OUTPUT_DIR="${SCRIPT_DIR}/release-output"
SKIP_FRONTEND=false
SKIP_BUILD=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }
die()       { log_error "$*"; exit 1; }

usage() {
    cat <<EOF
PyDataEase 构建发布脚本

用法: $0 [选项]

选项:
  -v, --version VERSION    版本号（默认从 pyproject.toml 读取）
  -o, --output DIR         输出目录（默认: ./release-output）
  --skip-frontend          跳过前端构建（使用已有 dist/）
  --skip-build             跳过 Docker 镜像构建（使用已有镜像）
  -h, --help               显示帮助信息

示例:
  $0                              # 自动版本号
  $0 -v 2.10.0                    # 指定版本号
  $0 -v 2.10.0 -o /tmp/release   # 指定输出目录
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -v|--version)  VERSION="$2"; shift 2 ;;
            -o|--output)   OUTPUT_DIR="$2"; shift 2 ;;
            --skip-frontend) SKIP_FRONTEND=true; shift ;;
            --skip-build)    SKIP_BUILD=true; shift ;;
            -h|--help)      usage; exit 0 ;;
            *)              die "未知参数: $1. 使用 -h 查看帮助." ;;
        esac
    done
}

detect_version() {
    if [[ -n "${VERSION}" ]]; then
        return
    fi
    local pyproject="${SCRIPT_DIR}/core/pydataease-backend/pyproject.toml"
    if [[ -f "${pyproject}" ]]; then
        VERSION=$(grep '^version = ' "${pyproject}" | head -1 | sed 's/version = "\(.*\)"/\1/')
        log_info "从 pyproject.toml 读取版本号: ${VERSION}"
    else
        VERSION="dev"
        log_warn "未找到 pyproject.toml，使用默认版本号: ${VERSION}"
    fi
}

check_prerequisites() {
    log_info "========== 检查构建环境 =========="

    command -v docker &>/dev/null || die "未找到 docker，请先安装 Docker"
    command -v git &>/dev/null || die "未找到 git"
    command -v tar &>/dev/null || die "未找到 tar"

    docker version --format '{{.Server.Version}}' &>/dev/null || die "Docker 服务未运行"

    if [[ "${SKIP_FRONTEND}" == "false" ]]; then
        command -v node &>/dev/null || die "未找到 node，前端构建需要 Node.js 18+"
        command -v npm &>/dev/null || die "未找到 npm"
    fi

    log_info "构建环境检查通过 ✓"
}

build_frontend() {
    log_info "========== 构建前端 =========="
    local frontend_dir="${SCRIPT_DIR}/core/core-frontend"

    if [[ "${SKIP_FRONTEND}" == "true" ]]; then
        if [[ -d "${frontend_dir}/dist" ]]; then
            log_info "跳过前端构建（使用已有 dist/）"
            return
        else
            die "--skip-frontend 但 dist/ 目录不存在"
        fi
    fi

    if [[ ! -d "${frontend_dir}" ]]; then
        die "前端目录不存在: ${frontend_dir}"
    fi

    log_info "安装前端依赖..."
    npm ci --prefix "${frontend_dir}"

    log_info "构建前端 (npm run build:distributed)..."
    npm run build:distributed --prefix "${frontend_dir}"

    if [[ -f "${frontend_dir}/dist/index.html" ]]; then
        log_info "前端构建完成 ✓"
    else
        die "前端构建失败：dist/index.html 不存在"
    fi
}

build_docker_images() {
    log_info "========== 构建 Docker 镜像 =========="

    if [[ "${SKIP_BUILD}" == "true" ]]; then
        log_info "跳过 Docker 镜像构建（使用已有镜像）"
        return
    fi

    # 构建后端镜像
    log_info "构建后端镜像 pydataease-app:${VERSION}..."
    docker build \
        --build-arg "VERSION=${VERSION}" \
        -t "pydataease-app:${VERSION}" \
        -f "${SCRIPT_DIR}/Dockerfile" \
        "${SCRIPT_DIR}"
    log_info "后端镜像构建完成 ✓"

    # 构建 Nginx 镜像
    log_info "构建 Nginx 镜像 pydataease-nginx:${VERSION}..."
    docker build \
        -t "pydataease-nginx:${VERSION}" \
        -f "${SCRIPT_DIR}/Dockerfile.nginx" \
        "${SCRIPT_DIR}"
    log_info "Nginx 镜像构建完成 ✓"

    # 拉取 PG 镜像
    log_info "拉取 PostgreSQL 镜像 pgvector/pgvector:pg16..."
    docker pull pgvector/pgvector:pg16
    log_info "PostgreSQL 镜像拉取完成 ✓"
}

assemble_release() {
    log_info "========== 组装发布包 =========="

    local pkg_dir="${OUTPUT_DIR}/pydataease-${VERSION}"

    log_info "发布目录: ${pkg_dir}"
    rm -rf "${pkg_dir}"
    mkdir -p "${pkg_dir}"/{bin/lib,conf/nginx,images,release}

    # 复制管理脚本
    log_info "复制管理脚本..."
    cp "${SCRIPT_DIR}/install.sh"    "${pkg_dir}/bin/"
    cp "${SCRIPT_DIR}/start.sh"      "${pkg_dir}/bin/"
    cp "${SCRIPT_DIR}/stop.sh"       "${pkg_dir}/bin/"
    cp "${SCRIPT_DIR}/upgrade.sh"    "${pkg_dir}/bin/"
    cp "${SCRIPT_DIR}/uninstall.sh"  "${pkg_dir}/bin/"
    cp "${SCRIPT_DIR}/status.sh"     "${pkg_dir}/bin/"
    chmod +x "${pkg_dir}/bin/"*.sh

    # 复制共享函数库
    cp "${SCRIPT_DIR}/lib/common.sh"  "${pkg_dir}/bin/lib/"
    cp "${SCRIPT_DIR}/lib/checks.sh"  "${pkg_dir}/bin/lib/"
    cp "${SCRIPT_DIR}/lib/docker.sh"  "${pkg_dir}/bin/lib/"
    cp "${SCRIPT_DIR}/lib/backup.sh"  "${pkg_dir}/bin/lib/"
    chmod +x "${pkg_dir}/bin/lib/"*.sh

    # 复制配置模板
    log_info "复制配置模板..."
    cp "${SCRIPT_DIR}/conf/install.env.example" "${pkg_dir}/conf/install.env.example"

    # 复制 docker-compose 模板
    cp "${SCRIPT_DIR}/conf/docker-compose.yml.template" "${pkg_dir}/conf/"

    # 复制 Nginx 配置
    cp "${SCRIPT_DIR}/conf/nginx/default.conf" "${pkg_dir}/conf/nginx/"

    # 导出 Docker 镜像
    log_info "导出 Docker 镜像（可能需要几分钟）..."
    docker save \
        "pydataease-app:${VERSION}" \
        "pydataease-nginx:${VERSION}" \
        pgvector/pgvector:pg16 \
        -o "${pkg_dir}/images/pydataease-images.tar"
    local tar_size
    tar_size=$(du -sh "${pkg_dir}/images/pydataease-images.tar" | cut -f1)
    log_info "镜像导出完成 (${tar_size}) ✓"

    # 写入版本文件
    echo "${VERSION}" > "${pkg_dir}/release/VERSION"

    # 创建安装入口脚本（根目录快捷方式，指向 bin/）
    cat > "${pkg_dir}/install.sh" <<'ENTRY'
#!/usr/bin/env bash
# PyDataEase 安装入口
# 请先编辑 conf/install.env.example 为 conf/install.env，修改配置后执行此脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/bin/install.sh" "$@"
ENTRY
    chmod +x "${pkg_dir}/install.sh"

    # 同样创建其他入口
    for cmd in start stop upgrade uninstall status; do
        cat > "${pkg_dir}/${cmd}.sh" <<ENTRY
#!/usr/bin/env bash
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
exec "\${SCRIPT_DIR}/bin/${cmd}.sh" "\$@"
ENTRY
        chmod +x "${pkg_dir}/${cmd}.sh"
    done

    # 创建使用说明
    cat > "${pkg_dir}/README.txt" <<EOF
PyDataEase ${VERSION} 安装包

安装步骤:
1. 复制 conf/install.env.example 为 conf/install.env
   cp conf/install.env.example conf/install.env

2. 编辑 conf/install.env，填写必改项:
   - DE_SECRET_KEY（JWT 密钥）
   - DE_SHARE_SECRET_KEY（分享 Token 密钥）
   - DE_ADMIN_PASSWORD（管理员初始密码）

3. 执行安装:
   ./install.sh

管理命令:
   ./start.sh      启动服务
   ./stop.sh       停止服务
   ./upgrade.sh    升级（需要新版本安装包）
   ./uninstall.sh  卸载（--purge 删除所有数据）
   ./status.sh     查看运行状态

默认端口: 8100
默认管理员: admin / <install.env 中设置的密码>

详细文档: https://github.com/dataease/pydataease
EOF

    log_info "发布包组装完成 ✓"
}

create_archive() {
    log_info "========== 创建压缩包 =========="

    local pkg_dir="${OUTPUT_DIR}/pydataease-${VERSION}"
    local archive="${OUTPUT_DIR}/pydataease-${VERSION}.tar.gz"

    if [[ -f "${archive}" ]]; then
        rm "${archive}"
    fi

    tar -czf "${archive}" -C "${OUTPUT_DIR}" "pydataease-${VERSION}"

    local archive_size
    archive_size=$(du -sh "${archive}" | cut -f1)
    log_info "压缩包: ${archive} (${archive_size}) ✓"
}

print_summary() {
    local pkg_dir="${OUTPUT_DIR}/pydataease-${VERSION}"
    local archive="${OUTPUT_DIR}/pydataease-${VERSION}.tar.gz"

    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${GREEN}  构建完成！${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
    echo "  版本:     ${VERSION}"
    echo "  发布目录: ${pkg_dir}"
    echo "  压缩包:   ${archive}"
    echo ""
    echo "  部署到生产服务器:"
    echo "    scp ${archive} user@server:/opt/module/"
    echo "    ssh user@server"
    echo "    cd /opt/module && tar -xzf pydataease-${VERSION}.tar.gz"
    echo "    cd pydataease-${VERSION}"
    echo "    cp conf/install.env.example conf/install.env"
    echo "    vim conf/install.env"
    echo "    ./install.sh"
    echo ""
}

main() {
    parse_args "$@"
    detect_version
    check_prerequisites
    build_frontend
    build_docker_images
    assemble_release
    create_archive
    print_summary
}

main "$@"
