#!/usr/bin/env bash
# chmod +x lib/docker.sh
# Docker Compose 操作函数库
set -euo pipefail

DOCKER_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DOCKER_LIB_DIR}/common.sh"

# 返回 docker-compose.yml 所在的 conf/ 目录路径
compose_dir() {
    local install_dir
    install_dir="$(get_install_dir)"
    echo "${install_dir}/conf"
}

# 执行 docker compose 命令
# 用法: compose_cmd [docker compose 子命令和参数...]
compose_cmd() {
    local compose_file
    compose_file="$(compose_dir)/docker-compose.yml"
    docker compose -f "${compose_file}" "$@"
}

# 启动所有服务（后台运行）
compose_up() {
    log_info "启动服务..."
    compose_cmd up -d
    log_info "服务已启动"
}

# 停止所有服务（不删除容器）
compose_stop() {
    log_info "停止服务..."
    compose_cmd stop
    log_info "服务已停止"
}

# 停止并删除所有容器
compose_down() {
    log_info "停止并删除所有容器..."
    compose_cmd down
    log_info "所有容器已删除"
}

# 等待健康检查通过（轮询 HTTP 接口）
# 超时时间默认 120 秒
wait_for_health() {
    local port="${DE_PORT:-8100}"
    local url="http://localhost:${port}/de2api/health"
    local timeout="${DE_HEALTH_TIMEOUT:-120}"
    local elapsed=0
    local interval=3

    log_info "等待服务健康检查通过 (超时: ${timeout}s, 端口: ${port})..."

    while (( elapsed < timeout )); do
        if curl -sf -o /dev/null "${url}" 2>/dev/null; then
            log_info "服务健康检查通过 ✓ (耗时 ${elapsed}s)"
            return 0
        fi
        sleep "${interval}"
        elapsed=$(( elapsed + interval ))
    done

    log_error "服务健康检查超时 (${timeout}s)"
    log_error "请检查日志: docker compose logs"
    return 1
}

# 加载离线镜像包
# 如果 DE_IMAGE_DIR 已设置且非空，则从该目录加载 .tar 文件
load_images() {
    if [[ -z "${DE_IMAGE_DIR:-}" ]]; then
        log_info "未设置 DE_IMAGE_DIR，跳过离线镜像加载（将使用在线拉取或已加载的镜像）"
        return 0
    fi

    if [[ ! -d "${DE_IMAGE_DIR}" ]]; then
        die "镜像目录 ${DE_IMAGE_DIR} 不存在"
    fi

    local tar_files
    tar_files=$(find "${DE_IMAGE_DIR}" -maxdepth 1 -name '*.tar' -type f 2>/dev/null)
    if [[ -z "${tar_files}" ]]; then
        log_warn "镜像目录 ${DE_IMAGE_DIR} 中未找到 .tar 文件"
        return 0
    fi

    log_info "从 ${DE_IMAGE_DIR} 加载离线镜像..."
    local count=0
    while IFS= read -r tar_file; do
        log_info "加载镜像: $(basename "${tar_file}")"
        docker load -i "${tar_file}"
        count=$((count + 1))
    done <<< "${tar_files}"
    log_info "已加载 ${count} 个镜像 ✓"
}

# 运行一次性容器命令
# 用法: run_oneoff [命令...]
run_oneoff() {
    log_info "执行一次性命令: $*"
    compose_cmd run --rm app "$@"
}
