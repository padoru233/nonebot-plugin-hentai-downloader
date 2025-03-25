import os
import httpx
from nonebot import logger, get_driver, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin.on import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message
from pathlib import Path
from .config import PluginConfig

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

plugin_config = PluginConfig()
plugin_cache_dir: Path = store.get_plugin_cache_dir()


__plugin_meta__ = PluginMetadata(
    name="本子下载插件",
    description="Nonebot本子下载",
    usage="下载jm",
    type="application",
    homepage="https://github.com/padoru233/nonebot-plugin-hentai-downloader",
    supported_adapters={"~onebot.v11"}
)


async def upload_group_file(bot, event, file: str, name: str):
    group_id = event.group_id
    try:
        await bot.upload_group_file(group_id=group_id, file="file:///" + file, name=name)
        return True
    except Exception as e:
        logger.error(event, f"上传群文件失败: {e}")

async def upload_private_file(bot, event, file: str, name: str):
    user_id = event.user_id
    try:
        await bot.upload_private_file(user_id=user_id, file="file:///" + file, name=name)
        return True
    except Exception as e:
        logger.error(event, f"上传私聊文件失败: {e}")

async def download_jm_pdf(comic_id: str):
    """
    通过API下载JM漫画PDF

    Args:
        comic_id: 漫画ID

    Returns:
        tuple: (pdf_path, pdf_name) 如果成功，否则 (None, None)
    """
    api_url = f"{plugin_config.jm_api_url}/download/{comic_id}/pdf"
    pdf_name = f"{comic_id}.pdf"

    try:
        # 使用nonebot_plugin_localstore创建的缓存目录
        pdf_path = os.path.join(str(plugin_cache_dir), pdf_name)

        # 确保缓存目录存在
        os.makedirs(plugin_cache_dir, exist_ok=True)

        logger.info(f"开始从API下载JM漫画 ID: {comic_id}")

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
                with open(pdf_path, 'wb') as f:
                    downloaded = 0
                    async for chunk in response.aiter_bytes(chunk_size=1024*1024):  # 1MB chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 可以在这里记录下载进度
                        if total_size > 0:
                            progress = downloaded / total_size * 100
                            logger.debug(f"下载进度: {progress:.2f}%")

        logger.info(f"JM漫画 ID: {comic_id} 下载完成，保存到: {pdf_path}")
        return pdf_path, pdf_name

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
async def got_comic_id(bot: Bot, matcher: Matcher, event: MessageEvent, comic_id: str = ArgPlainText()):
    if not comic_id.isdigit():
        await matcher.finish("您输入的漫画ID无效，操作已取消。")

    await matcher.send(f"开始下载ID为 {comic_id} 的漫画，请稍候...")

    # 使用API下载PDF
    pdf_path, pdf_name = await download_jm_pdf(comic_id)

    if pdf_path:
        # 上传PDF文件
        await matcher.send("PDF下载完成，正在上传...")

        # 根据消息类型选择上传方法
        if isinstance(event, GroupMessageEvent):
            if await upload_group_file(bot, event, pdf_path, pdf_name):
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成")
        elif isinstance(event, PrivateMessageEvent):
            if await upload_private_file(bot, event, pdf_path, pdf_name):
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成")

        # 删除临时文件
        try:
            os.remove(pdf_path)
            logger.info(f"临时文件已删除: {pdf_path}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {e}")

    else:
        await matcher.finish(f"下载失败，请检查ID {comic_id} 是否正确或API服务是否可用")
