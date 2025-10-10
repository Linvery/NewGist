from lxml import html
from .base import BaseSite
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def _hongkong_yesterday() -> str:
	yesterday = datetime.now(ZoneInfo("Asia/hong_kong")) - timedelta(days=1)
	return yesterday.strftime("%Y-%m-%d")

class MofcomBlgg(BaseSite):
    def extract_content(self, html_content: str) -> list[dict]:
        xml_path = '//*[@id="分页列表"]/div[1]/ul/li'
        tree = html.fromstring(html_content)
        content:list = tree.xpath(xml_path)  # type: ignore
        results: list[dict] = []
        for elem in content:
            try:
                title = elem.xpath('./a/text()')[0]
                date = elem.xpath('./span/text()')[0][1:-1] # 2025年9月25日
                date = datetime.strptime(date, "%Y-%m-%d").date().strftime("%Y-%m-%d")
                # 限制日期为上海时间 -1
                if date != _hongkong_yesterday():
                    continue
                results.append({
                    'title': title,
                    'date': date,
                })
            except (IndexError, ValueError) as exc:
                self.logger.warning("节点解析失败：%s", exc)
        return results
    
    def is_hit_anti(self, html_content: str) -> bool:
        if "DataDome Device Check" in html_content:
            self.logger.warning("检测到反爬机制：HTML 中出现 DataDome Device Check。")
            return True
        return False

def create(logger):
    return MofcomBlgg(logger)