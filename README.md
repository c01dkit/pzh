## Update Items

```shell
# When first init
git submodule update --init --recursive

uv sync

# After modifying yml files in /resource
uv run src/main.py

```
## Deploy 

git add .
git commit -m "xxx"
git push origin main:main

mkdocs gh-deploy --clean

## Acknowledgments 

Most of the blog configurations are from [Xiaokang2022](https://github.com/Xiaokang2022/)

The category menu plugin is from [TonyCrane](https://github.com/TonyCrane/).

## mkdocs

mkdocs, version 1.6.1 from ~/.local/lib/python3.10/site-packages/mkdocs (Python 3.10)