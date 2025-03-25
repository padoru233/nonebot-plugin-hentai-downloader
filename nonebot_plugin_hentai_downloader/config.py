from pydantic import BaseModel
from nonebot import get_driver

class PluginConfig(BaseModel):
    """本子下载插件配置"""
    jm_api_url: str = "http://localhost:9080"  # JM漫画API地址
