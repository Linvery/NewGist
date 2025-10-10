# NewsGist

> 华语读者的一站式新闻摘要流水线——自动抓取、结构化解析、AI 精炼、渠道分发，一条命令即可跑通。

## 目录

- [概览](#概览)
- [架构与数据流](#架构与数据流)
- [主要功能](#主要功能)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [运行与调度](#运行与调度)
- [日志与产物](#日志与产物)
- [测试](#测试)
- [扩展指南](#扩展指南)
- [FAQ & 故障排查](#faq--故障排查)
- [参考资料](#参考资料)

## 概览

NewsGist 面向需要快速掌握华尔街日报（WSJ）重点栏目与中国商务部公告的团队/个人，自动完成：

1. 打开目标栏目页面，模拟真人滚动，抓取完整 HTML。
2. 基于 XPath 解析出结构化新闻条目。
3. 调用支持 OpenAI 协议的模型生成中文摘要。
4. 通过微信桌面端将每日要闻推送给指定联系人。

整条流水线由 `main.py` 驱动，默认处理以下栏目的最新资讯：

| 模块 (`module`) | 描述 (`desc`) | URL |
| --- | --- | --- |
| `wsj_politics_policy` | 政治与政策 | https://www.wsj.com/politics/policy |
| `wsj_economy_global` | 全球经济 | https://www.wsj.com/economy/global |
| `wsj_world_china` | 中国相关 | https://www.wsj.com/world/china |
| `mofcom_blgg` | 商务部部令公告 | https://www.mofcom.gov.cn/zcfb/blgg/index.html |

## 架构与数据流

```
┌────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌───────────┐
│ main.py    │ → │ spider.Scraper │ → │ BaseSite子类 │ → │ AI.summarize_list │ → │ push.wechat │
└────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └───────────┘
      ↑                 │                │                  │                  │
      │                 └─ Zendriver ─────┴─ lxml/XPath ────┴─ OpenAI API ─────┴─ wxauto
      │
      └──── helper.logger & 配置
```

- `spider/spider.py`：基于 [Zendriver](https://github.com/holmium/zendriver) 的异步抓取器，包含真人滚动模拟与反爬兜底。
- `spider/site/*.py`：站点适配层，继承 `BaseSite`，统一实现 `extract_content` 与 `is_hit_anti`。
- `AI/ai.py`：封装 OpenAI 兼容接口，可按需切换模型或提示词。
- `push/wechat.py`：借助 `wxauto` 向指定好友/群聊发送生成的摘要。
- `push/slink.py`：可选的短链服务（默认在主流程中关闭）。

## 主要功能

- ✅ 自动滚动加载，规避首屏限制。
- ✅ XPath 级别的结构化提取（标题、摘要、作者、时间、链接）。
- ✅ 多线程批量调用 LLM，支持 DeepSeek / GPT 兼容模型。
- ✅ 微信桌面端自动推送，信息同步至联系人“每日要闻”。
- ⚙️ 自带日志与 HTML 留存，方便回溯。
- 🧩 站点、摘要、推送三层均可扩展。

## 快速开始

### 依赖要求

- Windows 10/11（`wxauto` 仅支持 Windows 桌面版微信）。
- Python 3.11+。
- 已安装最新 Chrome/Edge（Zendriver 调用系统浏览器）。
- 微信桌面端保持登录。

### 初始化步骤

```powershell
# 1. 克隆项目
git clone <your-repo-url>
cd NewsGist

# 2. （可选）创建并启用虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（见下文的 .env 模板）

# 5. 运行主流程
python main.py
```

首轮执行完成后，抓取到的 HTML 与日志可在 `logs/<module>/` 中查看，微信会收到“每日要闻”推送。

## 配置说明

在项目根目录创建 `.env`：

```env
# OpenAI 兼容接口（必填）
AI_BASE_URL=https://api.your-llm.com/v1
AI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 短链服务（可选，若未启用请保持默认值或删除）
SLINK_BASE_URL=https://slink.example.com
SLINK_TOKEN=your-slink-token
```

> 没有短链需求？保持 `push/slink.py` 默认状态即可。主流程中已注释相关调用，不会触发 ValueError。

其他配置提示：

- `main.py` 中的 `sites` 列表决定抓取顺序与目标栏目。
- 微信推送目标在 `push/wechat.py` 的 `sendMsg` 调用中指定（默认联系人名为“每日要闻”）。
- 如需切换模型或摘要风格，调整 `AI/ai.py` 内 `summarize_news` 的 `prompt` 与 `model`。

## 运行与调度

### 手动运行

PowerShell 中执行 `python main.py` 即可。

### 定时任务

1. 打开「任务计划程序」。
2. 创建基本任务 → 设置触发时间（如每日早上 7 点）。
3. 动作为“启动程序”，程序填写 `python`，参数填写完整脚本路径 `c:\path\to\NewsGist\main.py`。
4. 勾选“使用最高权限运行”，确保存储账号可访问浏览器与微信。

## 日志与产物

- `logs/<module>/<module>.log`：包含抓取、解析、AI 调用的运行记录。
- `logs/<module>/<module>.html`：保留对应栏目的原始 HTML，便于排查 XPath 失效、页面结构变更。
- 如需长期存档，可将 `logs/` 文件夹接入云盘或日志平台。

## 测试

项目附带一个示例网络测试 `tests/spider_test.py`，用于验证抓取器能否解析商务部公告页：

```powershell
pytest tests/spider_test.py::test_mofcom
```

> ⚠️ 该测试实时访问官网，可能受网络、反爬或页面改版影响。建议在本地调试时按需启用，CI/CD 环境请谨慎执行。

## 扩展指南

| 场景 | 操作 |
| --- | --- |
| 新增站点 | 在 `spider/site/` 新建模块并继承 `BaseSite`，实现 `extract_content` / `is_hit_anti`；随后在 `main.sites` 中注册。 |
| 自定义摘要 | 修改 `AI/ai.py` 的提示词或切换模型，例如使用 `gpt-4o-mini`、`deepseek-chat`。|
| 多渠道推送 | 在 `push/` 目录添加新模块（如 `telegram.py`），并在 `main.py` 中调用即可。|
| 使用短链 | 解开 `main.py` 中的注释，调用 `push.slink.shorten_url` 压缩链接。|

## FAQ & 故障排查

| 问题 | 可能原因 | 解决方案 |
| --- | --- | --- |
| `ValueError: Missing AI_BASE_URL or AI_API_KEY` | `.env` 未正确加载 | 确认键名无误，且 `.env` 位于项目根目录。|
| 抓取日志出现 `DataDome Device Check` | 触发目标站点反爬 | 降低频率、增加等待时间，或考虑代理/IP 轮换。|
| 微信未收到消息 | 未登录桌面微信、联系人名称不匹配 | 打开微信客户端并确认 `sendMsg` 的 `who` 参数与联系人完全一致。|
| 测试 `test_mofcom` 断言失败 | 官方公告标题更新 | 这是正常现象，更新断言或改用更稳健的判断逻辑。|

## 参考资料

- [Zendriver 文档](https://zendriver.readthedocs.io/)
- [wxauto 使用指南](https://github.com/cluic/wxauto)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

如需反馈或贡献，欢迎提交 Issue / PR，一起改进每日要闻工作流。
