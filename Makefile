# EdenxPrinter Makefile
# 作者: RBQ
# 版本: 1.0.0

.PHONY: help install install-dev test lint format clean run build docs

# 默认目标
help:
	@echo "EdenxPrinter 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install      - 安装生产依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  run          - 运行应用程序"
	@echo "  build        - 构建应用程序"
	@echo "  docs         - 生成文档"
	@echo "  setup-hooks  - 设置预提交钩子"
	@echo "  check-deps   - 检查依赖安全性"

# 虚拟环境设置
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# 创建虚拟环境
$(VENV):
	@echo "创建虚拟环境..."
	python3 -m venv $(VENV)
	@echo "虚拟环境创建完成"

# 安装生产依赖
install: $(VENV)
	@echo "安装生产依赖..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "依赖安装完成"

# 安装开发依赖
install-dev: install
	@echo "安装开发依赖..."
	$(PIP) install -r requirements-dev.txt
	@echo "开发依赖安装完成"

# 运行测试
test: $(VENV)
	@echo "运行测试..."
	$(PYTHON) -m pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov: $(VENV)
	@echo "运行测试并生成覆盖率报告..."
	$(PYTHON) -m pytest tests/ --cov --cov-report=html --cov-report=term
	@echo "覆盖率报告已生成到 htmlcov/ 目录"

# 代码检查
lint: $(VENV)
	@echo "运行代码检查..."
	$(PYTHON) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(PYTHON) -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	$(PYTHON) -m pylint --rcfile=.pylintrc src/ dialogs/ pages/ helper/ menus/ utils/ || true
	$(PYTHON) -m mypy . --ignore-missing-imports || true

# 代码格式化
format: $(VENV)
	@echo "格式化代码..."
	$(PYTHON) -m black .
	$(PYTHON) -m isort . --profile black
	@echo "代码格式化完成"

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo "清理完成"

# 运行应用程序
run: $(VENV)
	@echo "启动 EdenxPrinter..."
	$(PYTHON) main.py

# 构建应用程序
build: $(VENV)
	@echo "构建应用程序..."
	$(PIP) install pyinstaller
	$(PYTHON) -m PyInstaller --onefile --windowed --name EdenxPrinter main.py
	@echo "构建完成，可执行文件位于 dist/ 目录"

# 生成文档
docs: $(VENV)
	@echo "生成文档..."
	$(PIP) install sphinx sphinx-rtd-theme
	cd docs && make html
	@echo "文档已生成到 docs/_build/html/ 目录"

# 设置预提交钩子
setup-hooks: $(VENV)
	@echo "设置预提交钩子..."
	$(PIP) install pre-commit
	$(VENV)/bin/pre-commit install
	@echo "预提交钩子设置完成"

# 检查依赖安全性
check-deps: $(VENV)
	@echo "检查依赖安全性..."
	$(PIP) install safety
	$(VENV)/bin/safety check
	@echo "安全检查完成"

# 更新依赖
update-deps: $(VENV)
	@echo "更新依赖..."
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "依赖更新完成"

# 完整的开发环境设置
setup-dev: install-dev setup-hooks
	@echo "开发环境设置完成！"
	@echo "现在可以使用以下命令:"
	@echo "  make test     - 运行测试"
	@echo "  make lint     - 代码检查"
	@echo "  make format   - 代码格式化"
	@echo "  make run      - 运行应用"