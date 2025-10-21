from lxml import html
from .base import BaseSite
from datetime import datetime
from helper import today as _today

class MofcomZwgk(BaseSite):
    def extract_content(self, html_content: str) -> list[dict]:
        xml_path = '/html/body/div[1]/section/section/div[1]/div[1]/div[1]/ul[2]/li'
        tree = html.fromstring(html_content)
        content:list = tree.xpath(xml_path)  # type: ignore
        results: list[dict] = []
        for elem in content:
            try:
                title = elem.xpath('./a/text()')[0]
                date = elem.xpath('./p/i/text()')[0] # 10-21
                year = datetime.today().year
                date = datetime.strptime(f"{year}-{date}", "%Y-%m-%d").date().strftime("%Y-%m-%d")
                self.logger.debug("解析到标题: %s 日期: %s 香港今日日期：%s", title, date, _today())
                # 限制日期为今天
                if date != _today():
                    continue
                results.append({
                    'title': title,
                    'date': date,
                })
            except (IndexError, ValueError) as exc:
                self.logger.warning("节点解析失败：%s", exc)
        return results
    
    def is_hit_anti(self, html_content: str) -> bool:
        return False

def create(logger):
    return MofcomZwgk(logger)