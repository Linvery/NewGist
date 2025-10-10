from __future__ import annotations
from abc import ABC, abstractmethod
import logging

class BaseSite(ABC):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def configure_driver(self, options) -> None:
        """子类按需调整 driver 配置。参数可为 Selenium Options 或 Zendriver Config。"""
        return

    def on_driver_ready(self, driver) -> None:
        """driver 初始化完成后的可选钩子。"""
        return

    # 子类必须实现的方法
    @abstractmethod
    def extract_content(self, html_content: str) -> list[dict]:
        ...

    @abstractmethod
    def is_hit_anti(self, html_content: str) -> bool:
        ...