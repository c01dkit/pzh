
## 初次使用项目 

```shell
# When first init
git submodule update --init --recursive
uv sync

```

## 更新赛事

填充以下模板到`src/resource/events.yml`，然后运行`uv run src/main.py`即可。无需在意events.yml中的id字段。

```yaml
- name: # 赛事名称
  description: # 赛事简介
  url: # 赛事官网
  start_time: # 赛事开始时间，如1990-01-01 09:00:00
  end_time: # 赛事结束时间，如1990-01-01 09:00:00
  year: # 赛事年份，数字，如1990
  host: # 主办方，如cn
```

## 更新工具集

填充以下模板到`src/resource/tools.yml`，然后运行`uv run src/main.py`即可。无需在意tools.yml中的id字段。

```yaml
- name: # 工具名称
  url: # 工具地址
  description: # 工具描述，可以描述得详细一些，比如使用场景，以便搜索
  category: # 工具分类，可参考docs/tools已有分类，也可自定义新分类。脚本会自动合并相同分类
  tags: # 自定义工具核心标签
  - 旗语
  - 盲文
  - 摩斯
```

## 更新puzzle题目

TODO

## 更新密码表

上传图片到`docs/assets/images`，然后在`docs/graphs/index.md`中添加对应链接即可。

TODO 后续会更新自动管理方式。

## 网站调试与部署

```shell

# 网站调试
mkdocs serve

# 网站部署
git add .
git commit -m "xxx"
git push origin main:main
mkdocs gh-deploy --clean
```

## Acknowledgments 

Most of the blog configurations are from [Xiaokang2022](https://github.com/Xiaokang2022/)

The category menu plugin is from [TonyCrane](https://github.com/TonyCrane/).

## mkdocs

mkdocs, version 1.6.1 from ~/.local/lib/python3.10/site-packages/mkdocs (Python 3.10)