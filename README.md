<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="300" alt="logo"></a>
</div>


<div align="center">

## ✨ Nonebot2 本子下载插件 ✨

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/padoru233/nonebot-plugin-hentai-downloader.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-hentai-downloader">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-hentai-downloader.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="ruff">
</a>
<a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</a>
</div>

> [!IMPORTANT]
> **收藏项目** ～⭐️

<img width="100%" src="https://starify.komoridevs.icu/api/starify?owner=padoru233&repo=nonebot-plugin-hentai-downloader" alt="starify" />


## 📖 介绍

- 可拓展，暂时只接入了JM，自建 JM WEB API
  可上传加密压缩包/PDF
- 接入PICA WIP

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-hentai-downloader --upgrade
使用 **pypi** 源安装

    nb plugin install nonebot-plugin-hentai-downloader --upgrade -i "https://pypi.org/simple"
使用**清华源**安装

    nb plugin install nonebot-plugin-hentai-downloader --upgrade -i "https://pypi.tuna.tsinghua.edu.cn/simple"


</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details open>
<summary>uv</summary>

    uv add nonebot-plugin-hentai-downloader
安装仓库 master 分支

    uv add git+https://github.com/padoru233/nonebot-plugin-hentai-downloader@master
</details>

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-hentai-downloader
安装仓库 master 分支

    pdm add git+https://github.com/padoru233/nonebot-plugin-hentai-downloader@master
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-hentai-downloader
安装仓库 master 分支

    poetry add git+https://github.com/padoru233/nonebot-plugin-hentai-downloader@master
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_hentai_downloader"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项  | 必填  | 默认值 |   说明   |
| :-----: | :---: | :----: | :------: |
| jm_api_url |  是   |   http://localhost:9080   | JM API 的地址 |

## 🎉 使用
### 指令表
| 指令  | 权限  | 需要@ | 范围  |   说明   |
| :---: | :---: | :---: | :---: | :------: |
| 下载jm | 所有人  |  否   | 群聊/私聊  | 指令后+id，bot会询问下载方式 |

### 🎨 效果图
如果有效果图的话

### 🌹 鸣谢

- 由 https://github.com/hect0x7/JMComic-Crawler-Python 实现 JM API
- https://github.com/salikx/image2pdf 灵感来源
- https://github.com/lx1169732264/pica_crawler 实现 PICA API
