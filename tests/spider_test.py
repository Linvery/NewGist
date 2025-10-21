import pytest
from spider import spider

# 测试是否能成功爬取到页面，以wsj_economy_global为例
# def test_wsj_economy_global():
#     url = "https://www.wsj.com/economy/global"
#     module = "wsj_economy_global"
#     path = f"logs/{module}"
#     logger = spider.helper.logger(f"{path}/{module}.log")

#     try:
#         site_module = __import__(f"spider.site.{module}", fromlist=['create'])
#         create = getattr(site_module, "create")
#     except (ImportError, AttributeError) as e:
#         pytest.fail(f"模块 {module} 不存在或缺少 create(): {e}")

#     site_handler = create(logger)
#     scraper = spider.Scraper(url, site_handler, logger)
#     page_html = scraper.scrape()
    
#     assert page_html is not None and len(page_html) > 0, "Failed to scrape the page or empty content"

#     contents:list[dict] = site_handler.extract_content(page_html)
#     assert isinstance(contents, list) and len(contents) > 0, "No content extracted"
#     for item in contents:
#         assert 'title' in item and 'link' in item and 'desc' in item and 'date' in item, "Extracted item missing required fields"

# def test_mofcom_blgg():
#     url = "https://www.mofcom.gov.cn/zcfb/blgg/index.html"
#     module = "mofcom_blgg"
#     path = f"logs/{module}"
#     logger = spider.helper.logger(f"{path}/{module}.log")

#     try:
#         site_module = __import__(f"spider.site.{module}", fromlist=['create'])
#         create = getattr(site_module, "create")
#     except (ImportError, AttributeError) as e:
#         pytest.fail(f"模块 {module} 不存在或缺少 create(): {e}")

#     site_handler = create(logger)
#     scraper = spider.Scraper(url, site_handler, logger)
#     page_html = scraper.scrape()
    
#     assert page_html is not None and len(page_html) > 0, "Failed to scrape the page or empty content"

#     contents:list[dict] = site_handler.extract_content(page_html)
#     assert isinstance(contents, list) and len(contents) > 0, "No content extracted"
#     for item in contents:
#         assert 'title' in item and 'date' in item, "字段缺失"

#       # 示例标题，根据实际情况调整
#     assert contents[0]['title'] == "商务部公告2025年第64号 2026年食糖、羊毛、毛条进口关税配额实施细则","输出的标题不匹配"
#     assert contents[1]['title'] == "商务部 海关总署公告2025年第58号 公布对锂电池和人造石墨负极材料相关物项实施出口管制的决定","输出的标题不匹配"


def test_mofcom_zwgk():
    url = "https://www.mofcom.gov.cn/zwgk/index.html"
    module = "mofcom_zwgk"
    path = f"logs/{module}"
    logger = spider.helper.logger(f"{path}/{module}.log")

    try:
        site_module = __import__(f"spider.site.{module}", fromlist=['create'])
        create = getattr(site_module, "create")
    except (ImportError, AttributeError) as e:
        pytest.fail(f"模块 {module} 不存在或缺少 create(): {e}")

    site_handler = create(logger)
    scraper = spider.Scraper(url, site_handler, logger)
    page_html = scraper.scrape()
    
    assert page_html is not None and len(page_html) > 0, "Failed to scrape the page or empty content"

    contents:list[dict] = site_handler.extract_content(page_html)
    assert isinstance(contents, list) and len(contents) > 0, "No content extracted"
    for item in contents:
        assert 'title' in item and 'date' in item, "字段缺失"

      # 示例标题，根据实际情况调整
    assert contents[0]['title'] == "公布2026年化肥进口关税配额总量、分配原则及相关程序","输出的标题不匹配"
    assert contents[1]['title'] == "公布2026年原油非国营贸易进口允许量总量、申请条件和申请程序","输出的标题不匹配"