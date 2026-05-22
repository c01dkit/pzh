#!/bin/bash
echo -e "\033[0;32m构建网站...\033[0m"
uv run src/main.py

echo -e "\033[0;32m同步数据...\033[0m"
git add .
d=`date`
msg="Sync raw data at $d"
if [ $# -eq 1 ]
  then msg="$1"
fi
git commit -m "$msg"
git push origin main:main

echo -e "\033[0;32m部署网站...\033[0m"
uv run mkdocs gh-deploy --clean

# 同步到阿里云
if [ "$1" = "aliyun" ]; then
echo -e "\033[0;32m部署到阿里云...\033[0m"
SITE_FLAVOR=aliyun mkdocs build
rsync -av --delete ./site/ aliyun:/root/nginx_website/puzzlehunt_site/
fi