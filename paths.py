# paths.py
# from __future__ import annotations
import sys
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir

APP_NAME = "iOSRealRun-18"
APP_AUTHOR = "YourOrg"  # 可留空或写你的组织名

def app_base_dir() -> Path:
    """打包后指向临时解包目录(_MEIPASS)，开发时指向当前文件所在目录。"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # 假设 paths.py 在项目根 or 任一子模块中都 OK，用 cwd/文件父级都行
    return Path(__file__).resolve().parent

def resource_path(rel: str | Path) -> Path:
    """读取随包资源（默认配置/示例文件/图标等）"""
    return (app_base_dir() / rel).resolve()

def user_cfg_dir() -> Path:
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))

def user_data_dir_() -> Path:
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))
