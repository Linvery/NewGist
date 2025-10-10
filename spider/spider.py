from __future__ import annotations
import asyncio
import random
import sys
import time
import logging
import helper
from spider.site.base import BaseSite
import os
import zendriver as zd

class Scraper:
    def __init__(self, url: str, site: BaseSite, logger: logging.Logger | None = None) -> None:
        self.url = url
        self.site = site
        self.logger = logger or site.logger
        self._config = self._build_config()

    def _build_config(self) -> zd.Config:
        config = zd.Config()

        if not config.browser_args:
            config.browser_args = []
        config.browser_args.append("--incognito")

        self.site.configure_driver(config)
        return config

    def scrape(self) -> str:
        self.logger.info("开始抓取，目标 URL：%s", self.url)
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            return asyncio.run(self._scrape_async())
        except TimeoutError as e:
            self.logger.error("页面加载超时：%s", e)
            raise
        except Exception as e:
            self.logger.error("抓取过程中出现错误：%s", e)
            raise

    async def _scrape_async(self) -> str:
        browser = await zd.start(config=self._config)
        self.logger.info("Zendriver 浏览器初始化成功。")

        try:
            tab = await asyncio.wait_for(browser.get(self.url), timeout=30)
            self.site.on_driver_ready(tab)
            await tab  # 等待页面主要事件完成
            self.logger.info("页面已加载，等待内容...")
            await tab.wait(10)
            await self._simulate_human_scroll(tab)
            await tab.wait(5)

            page_html = await tab.get_content()
            if self.site.is_hit_anti(page_html):
                raise RuntimeError("触发反爬机制，抓取终止。")

            self.logger.info("抓取完成，准备关闭浏览器。")
            return page_html
        finally:
            await browser.stop()
            self.logger.info("浏览器已安全关闭。")

    async def _simulate_human_scroll(
        self,
        tab: zd.Tab,
        plateau_limit: int = 10,
        max_duration: int = 30,
    ) -> None:
        """通过非线性、带随机性的滚动行为模拟真人浏览。"""

        self.logger.info("开始模拟人类滚动...")

        current_offset = 0.0
        plateau_count = 0
        cycle = 0
        start_time = time.monotonic()

        while True:
            if time.monotonic() - start_time > max_duration:
                self.logger.warning("滚动超过最大持续时间 %.1f 秒，停止以避免无限循环。", max_duration)
                break

            viewport_height = 800
            progress_ratio = min(1.0, (cycle + 1) / plateau_limit)
            base_step = viewport_height * random.uniform(0.25, 0.6)
            eased_step = base_step * (0.5 + 0.5 * progress_ratio)
            jitter = random.uniform(-0.15, 0.15) * eased_step
            step = max(40.0, eased_step + jitter)

            await tab.scroll_down(int(step))
            current_offset += step
            self.logger.info(
                "滚动第 %d 次，下移 %.2f px，累计位移 %.2f px",
                cycle + 1,
                step,
                current_offset,
            )

            await tab.wait(random.uniform(0.2, 0.4))

            plateau_count += 1
            if plateau_count >= plateau_limit:
                self.logger.info("达到设定的滚动阈值，结束滚动。")
                break

            cycle += 1

