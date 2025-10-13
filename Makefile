build:
	rm -rf dist
	rm -rf *.egg-info
	uv run python -m build

upload:
	uv run twine upload --username __token__ dist/* 

image:
	docker build -t faster_app .