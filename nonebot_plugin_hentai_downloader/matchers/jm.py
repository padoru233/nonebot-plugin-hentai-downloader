import os
import jmcomic
from nonebot import logger
from pathlib import Path
from jmcomic import JmOption
import nonebot_plugin_localstore as store



# 使用插件提供的存储路径
DATA_DIR: Path  = store.get_plugin_data_dir()  # 插件数据目录
config_file: Path = store.get_plugin_config_file("option.yml")
jm_data_dir = str(DATA_DIR)

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)


async def jm2pdf(comic_id):
    """下载指定ID的漫画并转换为PDF (使用配置文件)"""

    try:
        jm_option = JmOption.from_file(str(config_file))
    except Exception as e:
        logger.error(f"加载配置文件 {config_file} 失败: {e}")
        jm_option = JmOption.default()

    jmcomic.download_album(comic_id, option=jm_option)

    # 获取漫画名称
    try:
        client = jm_option.new_jm_client()
        comic_info: JmAlbumDetail = client.get_album_detail(comic_id)
    except Exception as e:
        logger.exception(f"获取漫画信息失败: {e}")
        return None

    pdf_name = f"{comic_info.authoroname}.pdf"

    pdf_path = str(DATA_DIR / pdf_name)

    if pdf_path:
        logger.info(f"漫画 {comic_id} 已成功转换为PDF: {pdf_path}")
    else:
        logger.error(f"漫画 {comic_id} PDF转换失败")

    return pdf_path, pdf_name

if not os.path.exists(config_file):
    with open(config_file, "w", encoding="utf-8") as file:
        file.write(
            f"""dir_rule:
  base_dir: {jm_data_dir}
  rule: Bd_Aauthoroname
plugins:
  after_album:
    - plugin: img2pdf
      kwargs:
        pdf_dir: {jm_data_dir}
        filename_rule: Aauthoroname
"""
        )
