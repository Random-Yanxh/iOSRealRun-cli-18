import yaml
from pathlib import Path
from paths import user_data_dir_, resource_path

# 用户配置文件路径
USER_CFG = user_data_dir_() / "config.yaml"
DEFAULT_CFG_IN_PKG = resource_path("config.yaml")  # 打包内的默认配置

# 用户的 route.txt 文件路径
USER_ROUTE = user_data_dir_() / "route.txt"
DEFAULT_ROUTE_IN_PKG = resource_path("route.txt")  # 默认模板文件路径

def ensure_user_config() -> Path:
    """确保用户配置文件存在。如果不存在，从打包的默认文件初始化。"""
    # 确保用户目录存在
    USER_CFG.parent.mkdir(parents=True, exist_ok=True)
    if not USER_CFG.exists():
        if DEFAULT_CFG_IN_PKG.exists():
            USER_CFG.write_text(DEFAULT_CFG_IN_PKG.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            USER_CFG.write_text("", encoding="utf-8")
    return USER_CFG

def ensure_user_route() -> Path:
    """确保用户的 route.txt 文件存在。如果不存在，从打包的默认文件初始化。"""
    # 确保用户目录存在
    USER_ROUTE.parent.mkdir(parents=True, exist_ok=True)
    if not USER_ROUTE.exists():
        if DEFAULT_ROUTE_IN_PKG.exists():
            USER_ROUTE.write_text(DEFAULT_ROUTE_IN_PKG.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            USER_ROUTE.write_text("", encoding="utf-8")
    return USER_ROUTE

def load_config() -> dict:
    """加载用户配置。"""
    cfg_path = ensure_user_config()
    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

def save_config(data: dict) -> None:
    """保存用户配置。"""
    cfg_path = ensure_user_config()
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def load_route() -> str:
    """加载用户的 route.txt 内容。"""
    route_path = ensure_user_route()
    return route_path.read_text(encoding="utf-8")

def save_route(route_content: str) -> None:
    """保存用户的 route.txt 内容。"""
    route_path = ensure_user_route()
    route_path.write_text(route_content, encoding="utf-8")


class Config:
    def __init__(self):
        cfg_path = ensure_user_config()
        with open(cfg_path, 'r') as f:
            config = yaml.safe_load(f)
        for i in config:
            setattr(self, i, config[i])


        # 加载 routeConfig 配置
        # self.route_file = self.config.get('routeConfig', 'route.txt')


config = Config()