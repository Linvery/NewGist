import os

import requests
from dotenv import load_dotenv

load_dotenv()

slink_baseurl = os.getenv("SLINK_BASE_URL")
slink_token = os.getenv("SLINK_TOKEN")

if not slink_baseurl or not slink_token:
    raise ValueError("Missing SLINK_BASE_URL or SLINK_TOKEN environment variables.")

def shorten_url(long_url: str) -> str:
    try:
        response = requests.post(
            f"{slink_baseurl}/api/link/create",
            json={"url": long_url},
            headers={"Authorization": f"Bearer {slink_token}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("link"):
            return f"{slink_baseurl}/{data['link']['slug']}"
        else:
            raise ValueError(f"短链接创建失败: {data.get('message', 'Unknown error')}")
    except requests.RequestException as e:
        raise RuntimeError(f"短链接服务通信错误: {e}") from e
    
if __name__ == "__main__":
    long_url = "https://www.wsj.com/articles/eurozone-joblessness-rises-95125525"
    try:
        short_url = shorten_url(long_url)
        print(f"Shortened URL: {short_url}")
    except Exception as e:
        print(f"Error: {e}")