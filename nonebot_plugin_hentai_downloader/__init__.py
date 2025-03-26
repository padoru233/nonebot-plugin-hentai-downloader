import os
import httpx
import pyminizip
from nonebot import logger, get_driver, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin.on import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message
from pathlib import Path
from datetime import datetime
from .config import PluginConfig

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

plugin_config = PluginConfig()
plugin_cache_dir: Path = store.get_plugin_cache_dir()


__plugin_meta__ = PluginMetadata(
    name="本子下载插件",
    description="Nonebot2 本子下载",
    usage="下载jm",
    type="application",
    homepage="https://github.com/padoru233/nonebot-plugin-hentai-downloader",
    supported_adapters={"~onebot.v11"}
)


async def encrypt_zip(zip_file_path: str, password: str):
    """
    将未加密的 ZIP 文件打包进一个加密的 ZIP 文件，并替换原始文件
    """
    logger.info(f"开始加密 ZIP 文件并替换: {zip_file_path}")

    encrypted_zip_path = zip_file_path + ".encrypted"

    try:
        # 创建加密的 ZIP 文件
        pyminizip.compress(zip_file_path, None, encrypted_zip_path, password, 5)

        os.remove(zip_file_path)  # 删除原始 ZIP 文件
        os.rename(encrypted_zip_path, zip_file_path)  # 重命名加密文件为原始文件名

        logger.info(f"已成功加密 ZIP 文件并替换原始文件: {zip_file_path}")
    except Exception as e:
        logger.error(f"加密 ZIP 文件并替换原始文件失败: {e}")

async def upload_group_file(bot, event, file: str, name: str):
    try:
        await bot.upload_group_file(group_id=event.group_id, file="file:///" + file, name=name)
        return True
    except Exception as e:
        logger.error(f"上传群文件失败: {e}")

async def upload_private_file(bot, event, file: str, name: str):
    try:
        await bot.upload_private_file(user_id=event.user_id, file="file:///" + file, name=name)
        return True
    except Exception as e:
        logger.error(f"上传私聊文件失败: {e}")

async def download_jm_pdf(comic_id: str):
    """
    通过API下载JM漫画PDF
    """
    api_url = f"{plugin_config.jm_api_url}/download/{comic_id}/pdf"
    pdf_name = f"{comic_id}.pdf"
    return await _download_jm_file(api_url, pdf_name, comic_id)

async def download_jm_zip(comic_id: str):
    """
    通过API下载JM漫画ZIP
    """
    api_url = f"{plugin_config.jm_api_url}/download/{comic_id}/zip"
    zip_name = f"{comic_id}.zip"
    return await _download_jm_file(api_url, zip_name, comic_id)

async def _download_jm_file(api_url: str, file_name: str, comic_id: str):
    """
    通用下载JM漫画文件 (PDF or ZIP)
    """
    try:
        # 使用nonebot_plugin_localstore创建的缓存目录
        file_path = os.path.join(str(plugin_cache_dir), file_name)

        # 确保缓存目录存在
        os.makedirs(plugin_cache_dir, exist_ok=True)

        logger.info(f"开始从API下载JM漫画 ID: {comic_id}，URL: {api_url}")

        async with httpx.AsyncClient(timeout=600) as client:  # 设置10分钟超时
            # 使用流式下载以处理大文件
            async with client.stream("GET", api_url) as response:
                if response.status_code != 200:
                    error_msg = await response.aread()
                    logger.error(f"下载失败: {response.status_code} - {error_msg}")
                    return None, None

                # 获取文件大小（如果服务器提供）
                total_size = int(response.headers.get('content-length', 0))

                # 写入文件
                with open(file_path, 'wb') as f:
                    downloaded = 0
                    async for chunk in response.aiter_bytes(chunk_size=1024*1024):  # 1MB chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 可以在这里记录下载进度
                        if total_size > 0:
                            progress = downloaded / total_size * 100
                            logger.debug(f"下载进度: {progress:.2f}%")

        logger.info(f"JM漫画 ID: {comic_id} 下载完成，保存到: {file_path}")
        return file_path, file_name

    except Exception as e:
        logger.error(f"下载JM漫画 ID: {comic_id} 时发生错误: {e}")
        return None, None


jm_download = on_command(
    "下载jm",
    priority=10,
    block=False
)

@jm_download.handle()
async def handle_jm_download(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    comic_id = args.extract_plain_text().strip()

    if comic_id.isdigit():
        matcher.set_arg("comic_id", Message(comic_id))

@jm_download.got("comic_id", prompt="请提供要下载的JM漫画ID（纯数字）：")
async def got_comic_id(matcher: Matcher, comic_id: str = ArgPlainText()):
    if not comic_id.isdigit():
        await matcher.finish("您输入的漫画ID无效，操作已取消。")

    matcher.set_arg("comic_id", comic_id) # Store comic_id as str, easier to use later
    await matcher.send(f"您要下载的漫画ID是：{comic_id}，请选择下载方式：\n1. zip (加密)\n2. pdf")

@jm_download.got("download_format")
async def got_download_format(bot: Bot, matcher: Matcher, event: MessageEvent, download_format: str = ArgPlainText()):
    if download_format not in ["1", "2"]:
        await matcher.finish("下载方式选择无效，操作已取消。请选择 1 或 2。")

    comic_id = matcher.get_arg("comic_id")
    if download_format == "1":
        matcher.set_arg("download_format", "zip")
        await matcher.send(f"您选择了 zip 下载，zip 压缩包密码为漫画ID：{comic_id}，开始下载...")
        file_path, file_name = await download_jm_zip(comic_id)
        if file_path:
            await encrypt_zip(file_path, comic_id) # 加密ZIP
    elif download_format == "2":
        matcher.set_arg("download_format", "pdf")
        await matcher.send(f"您选择了 pdf 下载，开始下载...")
        file_path, file_name = await download_jm_pdf(comic_id)
    else:
        await matcher.finish("未知的下载格式，操作已取消。")
        return

    if file_path:
        await matcher.send(f"{matcher.get_arg('download_format').upper()} 下载完成，正在上传...")

        if isinstance(event, GroupMessageEvent):
            if await upload_group_file(bot, event, file_path, file_name):
                password_message = f"，密码为 {comic_id}" if matcher.get_arg("download_format") == "zip" else ""
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成，格式为 {matcher.get_arg('download_format')}{password_message}")
        elif isinstance(event, PrivateMessageEvent):
            if await upload_private_file(bot, event, file_path, file_name):
                password_message = f"，密码为 {comic_id}" if matcher.get_arg("download_format") == "zip" else ""
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成，格式为 {matcher.get_arg('download_format')}{password_message}")

        try:
            os.remove(file_path)
            logger.info(f"临时文件已删除: {file_path}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {e}")
    else:
        await matcher.finish(f"下载失败，请检查ID {comic_id} 是否正确或API服务是否可用")
