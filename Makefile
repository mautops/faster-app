clean:
	rm -rf dist
	rm -rf *.egg-info

build:
	uv python -m build

upload:
	uv run twine upload --username __token__ dist/* 