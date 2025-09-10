#!/bin/bash
# EdenxPrinter 启动脚本
# 作者: RBQ
# 版本: 1.0.0

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

log_info "EdenxPrinter 启动脚本"
log_info "工作目录: $SCRIPT_DIR"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装，请先安装 Python 3.9+"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log_info "Python 版本: $PYTHON_VERSION"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    log_info "创建虚拟环境..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        log_success "虚拟环境创建成功"
    else
        log_error "虚拟环境创建失败"
        exit 1
    fi
fi

# 检查依赖是否需要安装
if [ ! -f "venv/pyvenv.cfg" ] || [ "requirements.txt" -nt "venv/pyvenv.cfg" ]; then
    log_info "安装/更新依赖包..."
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        log_success "依赖包安装完成"
    else
        log_error "依赖包安装失败"
        exit 1
    fi
else
    log_info "依赖包已是最新版本"
fi

# 检查主程序文件是否存在
if [ ! -f "main.py" ]; then
    log_error "main.py 文件不存在"
    exit 1
fi

# 启动程序
log_info "启动 EdenxPrinter..."
venv/bin/python main.py

# 检查程序退出状态
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    log_success "程序正常退出"
else
    log_error "程序异常退出，退出代码: $EXIT_CODE"
fi

exit $EXIT_CODE