from importlib import import_module
from spider import spider
import helper
import os
from tenacity import retry, stop_after_attempt, wait_fixed,retry_if_not_exception_type
from AI import ai
from push import wechat, slink
import datetime

sites: list[dict] = [
    {"url": "https://www.wsj.com/politics/policy","desc": "政治与政策", "module": "wsj_politics_policy"},
    {"url": "https://www.wsj.com/economy/global","desc": "全球经济", "module": "wsj_economy_global"},
    {"url": "https://www.wsj.com/world/china", "desc": "中国相关", "module": "wsj_world_china"},
    {"url": "https://www.mofcom.gov.cn/zcfb/blgg/index.html", "desc": "中国商务部部令公告", "module": "mofcom_blgg"},
]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2),
       retry=retry_if_not_exception_type(ImportError))
def main(url: str, module: str, desc: str) -> None:
    path = os.path.join(helper.get_current_directory(), "logs", module)
    logger = helper.logger(f"{path}/{module}.log")

    try:
        # 直接导入并校验 create 是否存在
        site_module = import_module(f"spider.site.{module}")
        create = getattr(site_module, "create")  # 若无此属性会抛 AttributeError
    except (ImportError, AttributeError) as e:
        # 统一转为 ImportError，这样 tenacity 不会重试，逻辑与原来一致
        raise ImportError(f"模块 {module} 不存在或缺少 create(): {e}") from e

    try:
        site_handler = create(logger)

        scraper = spider.Scraper(url, site_handler, logger)
        page_html = scraper.scrape()
        

        os.makedirs(path, exist_ok=True)
        html_path = os.path.join(path, f"{module}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_html)
            
        contents:list[dict] = site_handler.extract_content(page_html)
        logger.info("提取的内容: %s", contents)
        
        # 经过ai处理内容
        today = datetime.date.today().strftime("%Y年%m月%d日")
        
        # 短链服务 暂时不添加
        # for news in contents:
        #     news["link"] = slink.shorten_url(news["link"])
        
        ai_summarys = ai.summarize_list(contents)
        summarys = f"{today} {desc} 要闻: \n\n"
        _num = 1
        for summary in ai_summarys:
            summarys += f"{_num}. {summary}\n\n"
            _num += 1
        logger.info("生成的摘要: %s", summarys)
        wechat.sendMsg(summarys, "每日要闻")
    except Exception as e:
        logger.error("An error occurred in main.py: %s", e)
        raise


if __name__ == "__main__":
    for site in sites:
        main(site["url"], site["module"], site["desc"])