.PHONY: help install dev test test-unit test-integration test-coverage lint format clean docker-build docker-up docker-down

help:
	@echo "兴宇坤一协同决策支持系统 V1.0 - 开发命令"
	@echo ""
	@echo "设置与安装："
	@echo "  make install          安装项目依赖"
	@echo "  make dev              安装开发依赖"
	@echo ""
	@echo "测试："
	@echo "  make test             运行所有测试"
	@echo "  make test-unit        运行单元测试"
	@echo "  make test-integration 运行集成测试"
	@echo "  make test-coverage    生成覆盖率报告"
	@echo ""
	@echo "代码质量："
	@echo "  make lint             代码风格检查"
	@echo "  make format           自动代码格式化"
	@echo "  make quality          运行完整质量检查"
	@echo ""
	@echo "应用运行："
	@echo "  make run              本地运行应用"
	@echo "  make run-debug        调试模式运行"
	@echo ""
	@echo "Docker："
	@echo "  make docker-build     构建 Docker 镜像"
	@echo "  make docker-up        启动 Docker 容器"
	@echo "  make docker-down      停止 Docker 容器"
	@echo ""
	@echo "清理："
	@echo "  make clean            清理临时文件"

# 安装
install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# 测试
test: test-unit test-integration test-coverage

test-unit:
	pytest tests/test_infochain.py tests/test_chaingraph.py tests/test_briefengine.py -v

test-integration:
	pytest tests/test_integration.py -v --tb=short

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# 代码质量
lint:
	flake8 src tests
	mypy src --ignore-missing-imports

format:
	black src tests
	isort src tests

quality:
	@bash scripts/run_quality_checks.sh

# 应用运行
run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

run-debug:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-build:
	cd deploy/docker && docker-compose build

docker-up:
	cd deploy/docker && docker-compose up -d

docker-down:
	cd deploy/docker && docker-compose down

docker-logs:
	cd deploy/docker && docker-compose logs -f app

# 清理
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name 'htmlcov' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name '.venv' -not -path './.venv' -prune
	rm -rf build dist *.egg-info

.DEFAULT_GOAL := help
