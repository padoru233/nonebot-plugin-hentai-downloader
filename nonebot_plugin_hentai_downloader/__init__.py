import os
from nonebot import logger, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin.on import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="本子下载插件",
    description="Nonebot本子下载",
    usage="下载jm",
    type="application",
    homepage="https://github.com/padoru233/nonebot-plugin-hentai-downloader",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={"author": "padoru233"},
)


async def upload_group_file(bot, group_id: int, file: str, name: str):
    try:
        await bot.upload_group_file(group_id=group_id, file=file, name=name)
        return True
    except Exception as e:
        logger.error(f"上传群文件失败: {e}")
        return False

async def upload_private_file(bot, user_id: int, file: str, name: str):
    try:
        await bot.upload_private_file(user_id=user_id, file=file, name=name)
        return True
    except Exception as e:
        logger.error(f"上传私聊文件失败: {e}")
        return False


jm_download = on_command(
    "下载jm",
    priority=5,
    block=True
)

@jm_download.handle()
async def handle_jm_download(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    comic_id = args.extract_plain_text().strip()

    if comic_id.isdigit():
        matcher.set_arg("comic_id", Message(comic_id))

@jm_download.got("comic_id", prompt="请提供要下载的JM漫画ID（纯数字）：")
async def got_comic_id(bot: Bot, matcher: Matcher, event: MessageEvent, comic_id: str = ArgPlainText()):
    if not comic_id.isdigit():
        await jm_download.finish("您输入的漫画ID无效，操作已取消。")

    await jm_download.send(f"开始下载ID为 {comic_id} 的漫画，请稍候...")

    try:
        from .matchers.jm import jm2pdf  # 导入jm2pdf函数
        pdf_path, file_name = await jm2pdf(comic_id)

        if pdf_path and os.path.exists(pdf_path):
            # 上传PDF文件
            await matcher.send("PDF转换完成，正在上传...")

            # 根据消息类型选择上传方法
            if isinstance(event, GroupMessageEvent):
                await upload_group_file(bot, event.group_id, pdf_path, file_name)
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成")
            elif isinstance(event, PrivateMessageEvent):
                await upload_private_file(bot, event.user_id, pdf_path, file_name)
                await matcher.finish(f"本子 {comic_id} 已下载并上传完成")

        else:
            await matcher.finish("PDF转换失败")
    except Exception as e:
        await matcher.finish(f"下载或转换过程中出错：{str(e)}")
