
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

在`src/resources/puzzle-configs`目录下保存的yml文件都会被解析，其中每题的格式为：

```yaml
- event_id: # 这里填写该题目对应的赛事的id
  tool_ids: # 这里用列表填写该题目可能用到的工具的id
  title: # 题目名称
  round: # 题目所在区（也可留空）
  topics: # 这里用列表填写该题目涉及的主题（也可留空）
  author: # 出题人（也可留空）
  extractions: # 这里用列表填写该题目涉及的提取方式（也可留空）
  ft: # 这里填写flavor text
  note: # 这里填写一些备注，主要是说明一下本网站呈现方式和源网站的区别
  hints:
  - question: 我毫无头绪！
    answer: null
  - question: 该如何提取？
    answer: null
  milestones: null
  answer: # 答案
  ready: false # 题解写好了就改成True
```

建议以赛事为单位来保存yml文件。然后运行main.py，会在`src/resources/puzzles`目录下生成题解模板，同时yml文件也会更新puzzle的id。根据id找到对应的`main.md`文件进行编辑即可。完成后将`ready`改为true，再次运行main.py即可。

**注意：对于ready为false的题目，如果在题解未完全写完的情况下更新了题解模板文件（src/resources/puzzles/template.md），会导致题解被强行覆盖。请确保修改题解模板文件前题解均已完成。**

## 更新密码表

上传图片到`docs/assets/images`，然后在`docs/graphs/index.md`中添加对应链接即可。

TODO 后续会更新自动管理方式。

## 网站调试与部署

```shell

# 网站调试
uv run mkdocs serve

# 网站部署
git add .
git commit -m "xxx"
git push origin main:main
uv run mkdocs gh-deploy --clean
```

## Acknowledgments 

Most of the blog configurations are from [Xiaokang2022](https://github.com/Xiaokang2022/)

The category menu plugin is from [TonyCrane](https://github.com/TonyCrane/).

## mkdocs

mkdocs, version 1.6.1 from ~/.local/lib/python3.10/site-packages/mkdocs (Python 3.10)