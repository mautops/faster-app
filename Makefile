.PHONY: clean build upload image docs-serve docs-build docs-deploy docs-clean test test-cov test-verbose lint lint-fix format typecheck

clean:
	@echo "🧹 清理构建产物和临时文件..."
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@rm -rf dist build site
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@rm -rf htmlcov .coverage .coverage.* coverage.xml
	@rm -rf *.egg-info
	@echo "✅ 清理完成"

build:
	rm -rf dist
	rm -rf *.egg-info
	uv run python -m build

upload:
	uv run twine upload --username __token__ dist/*

image:
	docker build -t faster_app .

# 文档相关命令
docs-serve:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build

docs-deploy:
	uv run mkdocs build
	uv run mkdocs gh-deploy --force --clean

docs-clean:
	rm -rf site

# 测试相关命令
test:
	uv run pytest tests/

test-cov:
	uv run pytest tests/ --cov=faster_app --cov-report=html --cov-report=term

test-verbose:
	uv run pytest tests/ -v

# 代码质量相关命令
lint:
	uv run ruff check faster_app/

lint-fix:
	uv run ruff check --fix faster_app/

format:
	uv run ruff format faster_app/

typecheck:
	uv run mypy faster_app/
