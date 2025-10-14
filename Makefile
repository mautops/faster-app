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