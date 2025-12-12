# Makefile for AICraft Client

.PHONY: help install dev test lint format clean build run

help:
	@echo "AICraft Client - 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make dev        - 安装开发依赖"
	@echo "  make test       - 运行测试"
	@echo "  make lint       - 代码检查"
	@echo "  make format     - 代码格式化"
	@echo "  make clean      - 清理临时文件"
	@echo "  make build      - 打包应用"
	@echo "  make run        - 运行应用"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=.

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint **/*.py

format:
	black . --line-length 100

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

build:
	pyinstaller build.spec

run:
	python main.py
