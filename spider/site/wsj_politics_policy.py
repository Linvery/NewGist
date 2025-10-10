from __future__ import annotations
from lxml import html
from .base import BaseSite

class WSJPoliticsPolicy(BaseSite):
    def extract_content(self, html_content: str) -> list[dict]:
        xml_path = '/html/body/div[1]/div/main/div[3]/div[2]/div[1]/div/div[2]/div'
        tree = html.fromstring(html_content)
        content:list = tree.xpath(xml_path)  # type: ignore
        results: list[dict] = []
        for elem in content:
            try:
                link = elem.xpath('.//h3/a/@href')[0]
                title = elem.xpath('.//h3/a/div/text()')[0]
                desc = elem.xpath(".//p[@data-testid='flexcard-text']//text()")[0]
                author_list = elem.xpath('.//div[@data-testid="byline"]/a/span/span/text()')
                author = ''.join(author_list) if author_list else '未知作者'
                date = elem.xpath('.//p[@data-testid="timestamp-text"]/text()')[0]
                results.append({
                    'title': title,
                    'link': link,
                    'desc': desc,
                    'author': author,
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
    return WSJPoliticsPolicy(logger)