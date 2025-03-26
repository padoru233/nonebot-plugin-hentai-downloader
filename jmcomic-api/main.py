import os
import shutil
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import jmcomic
from jmcomic import JmOption
import yaml
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="JMComic API",
    description="API for downloading comics from JMComic",
    version="0.2.0"
)

# 定义存储目录
BASE_DIR = '/app'
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
CONFIG_DIR = os.path.join(BASE_DIR, 'configs')

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# 创建不同插件的配置文件
def create_config_files():
    # PDF配置
    pdf_config = {
        "dir_rule": {
            "base_dir": TEMP_DIR,
            "rule": "Bd_Aid"
        },
        "download": {
            "image": {
                "suffix": ".jpg"
            }
        },
        "plugins": {
            "after_album": [
                {
                    "plugin": "img2pdf",
                    "kwargs": {
                        "pdf_dir": DOWNLOAD_DIR,
                        "filename_rule": "Aid"
                    }
                }
            ]
        }
    }

    # ZIP配置
    zip_config = {
        "dir_rule": {
            "base_dir": TEMP_DIR,
            "rule": "Bd_Aid"
        },
        "download": {
            "image": {
                "suffix": ".jpg"
            }
        },
        "plugins": {
            "after_album": [
                {
                    "plugin": "zip",
                    "kwargs": {
                        "level": "album",
                        "filename_rule": "Aid",
                        "zip_dir": DOWNLOAD_DIR,
                        "delete_original_file": True
                    }
                }
            ]
        }
    }

    # 保存配置文件
    with open(os.path.join(CONFIG_DIR, "pdf_option.yml"), "w") as f:
        yaml.dump(pdf_config, f)

    with open(os.path.join(CONFIG_DIR, "zip_option.yml"), "w") as f:
        yaml.dump(zip_config, f)

# 创建配置文件
create_config_files()

# 辅助函数：清理特定ID的临时文件夹
def cleanup_temp_dir(comic_id: int):
    shutil.rmtree(os.path.join(TEMP_DIR, str(comic_id)), ignore_errors=True)

# 后台任务：延迟删除文件
async def delete_file_task(file_path: str, delay: int = 600):
    """异步后台任务：在延迟后删除文件。"""
    logging.info(f"后台任务：将在{delay}秒后删除文件 {file_path}")
    await asyncio.sleep(delay)
    try:
        os.remove(file_path)
        logging.info(f"后台任务：文件 {file_path} 已成功删除。")
    except Exception as e:
        logging.error(f"后台任务：删除文件 {file_path} 时出错：{e}")

def iterfile(file_path):
    with open(file_path, "rb") as file:
        yield from file


@app.get("/download/{comic_id}/pdf")
async def download_comic_pdf(comic_id: int, background_tasks: BackgroundTasks):
    """
    Download a comic by ID and return as PDF
    """
    try:
        # 加载PDF配置
        pdf_config = os.path.join(CONFIG_DIR, "pdf_option.yml")
        jm_option = JmOption.from_file(pdf_config)

        pdf_filename = f"{comic_id}.pdf"
        pdf_path = os.path.join(DOWNLOAD_DIR, pdf_filename)

        # 执行下载
        jmcomic.download_album(comic_id, option=jm_option)
        logging.info(f"Comic {comic_id} downloaded.")

        # 清理特定ID的临时目录
        cleanup_temp_dir(comic_id)

        # 获取生成的PDF文件
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")

        response = StreamingResponse(iterfile(pdf_path), media_type='application/pdf')
        background_tasks.add_task(delete_file_task, pdf_path, delay=600)

        return response

    except Exception as e:
        logging.error(f"Error downloading comic {comic_id}: {str(e)}")
        # 发生错误时清理特定ID的临时目录
        cleanup_temp_dir(comic_id)
        raise HTTPException(status_code=500, detail=f"Error downloading comic: {str(e)}")

@app.get("/download/{comic_id}/zip")
async def download_comic_zip(comic_id: int, background_tasks: BackgroundTasks):
    """
    Download a comic by ID and return as ZIP
    """
    try:
        # 加载ZIP配置
        zip_config = os.path.join(CONFIG_DIR, "zip_option.yml")
        jm_option = JmOption.from_file(zip_config)

        zip_filename = f"{comic_id}.zip"
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)

        # 执行下载
        jmcomic.download_album(comic_id, option=jm_option)
        logging.info(f"Comic {comic_id} downloaded.")

        # 清理特定ID的临时目录
        cleanup_temp_dir(comic_id)

        # 获取生成的ZIP文件
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="ZIP file not found")
       
        response = StreamingResponse(iterfile(zip_path), media_type='application/zip')
        background_tasks.add_task(delete_file_task, zip_path, delay=600)

        return response

    except Exception as e:
        # 发生错误时清理特定ID的临时目录
        cleanup_temp_dir(comic_id)
        raise HTTPException(status_code=500, detail=f"Error downloading comic: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 9080))
    uvicorn.run(app, host="127.0.0.1", port=port)
