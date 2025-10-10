import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.getenv("AI_BASE_URL")
api_key = os.getenv("AI_API_KEY")

if not base_url or not api_key:
    raise ValueError("Missing AI_BASE_URL or AI_API_KEY environment variables.")

def generate_text(prompt,user_text, model="gpt-4o-mini") -> str|None:
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ],
        stream=False
    )
    return response.choices[0].message.content

def summarize_news(news:dict)-> str:
    desc = news.get("desc", "无")
    prompt = """
    请你作为一个新闻摘要生成器，基于提供的消息生成一个简洁的中文摘要。

    输出格式要求：
    标题
    时间
    
    示例：
    欧元区失业率上升但仍接近历史低点
    2025年10月2日
    """
    story = f"\nTitle: {news['title']}\nDescription: {desc}\nDate: {news['date']}\n"
    result = generate_text(prompt,story,model="deepseek-chat")
    return result

def summarize_list(news_list:list[dict])-> list[str]:
    # 多线程处理
    summaries = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_news = {executor.submit(summarize_news, news): news for news in news_list}
        for future in as_completed(future_to_news):
            news = future_to_news[future]
            try:
                summary = future.result()
                summaries.append(summary)
            except Exception as e:
                print(f"AI线程错误 {news['title']}: {e}")
    return summaries

if __name__ == "__main__":
    news = [{'title': 'China’s Rare-Earth Escalation Threatens Trade Talks—and the Global Economy', 'link': 'https://www.wsj.com/world/china/china-trade-rare-earth-restrictions-ai-c2535244?mod=china_news_article_pos1', 'desc': 'President Trump says the administration is weighing a U.S. response to Beijing’s newest restrictions.', 'author': 'Amrith RamkumarLingling Wei', 'date': '6 hours ago'}, {'title': 'U.K. Government Accused of Scuttling China Spying Case', 'link': 'https://www.wsj.com/world/china/u-k-government-accused-of-scuttling-china-spying-case-2e6599a9?mod=china_news_article_pos2', 'desc': 'The case against a parliamentary researcher and one other person was dropped after the government didn’t define China as a threat.', 'author': 'Max Colchester', 'date': '17 hours ago'}, {'title': 'China Tightens Grip on Rare Earths Ahead of Expected Trump-Xi Meeting', 'link': 'https://www.wsj.com/economy/trade/china-imposes-new-controls-over-rare-earth-exports-35a4b106?mod=china_news_article_pos3', 'desc': 'Beijing tightened its control over sectors crucial to making high-tech products including electric vehicles and jet fighters, threatening to reignite trade tensions with the U.S.', 'author': 'Hannah Miao', 'date': '20 hours ago'}, {'title': 'How China Threatens to Force Taiwan Into a Total Blackout', 'link': 'https://www.wsj.com/world/asia/chinese-blockade-taiwan-d5b241c7?mod=china_news_article_pos4', 'desc': 'A Chinese blockade would quickly deplete resources on an island that depends on imported fuel.', 'author': 'James T. AreddyJoyu WangRoque Ruiz', 'date': 'October 7, 2025'}, {'title': 'How China Secretly Pays Iran for Oil and Avoids U.S. Sanctions', 'link': 'https://www.wsj.com/world/middle-east/how-china-secretly-pays-iran-for-oil-and-avoids-u-s-sanctions-b6f1b71e?mod=china_news_article_pos5', 'desc': 'A hidden funding conduit has deepened economic ties between the two U.S. rivals in defiance of Washington’s efforts to isolate Tehran.', 'author': 'Laurence NormanJames T. Areddy', 'date': 'October 5, 2025'}]
    summaries = summarize_list(news)
    for summary in summaries:
        print(summary)