from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from datetime import datetime
import json

# 配置 API Key 和 Base URL
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 定义提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", """
# 角色
你是一个资深搜索大师，根据用户提供的网页地址和内容，总结信息并以指定 JSON 格式返回结果。

## 技能
### 技能 1: 总结内容
1. 根据提供的网页地址和内容进行总结；
2. 对结果严格按照以下 JSON 格式回复（不需要包含 "date" 字段，我会在代码中添加当前日期）：

==示例回复==
{{
  "title": "AI日报：腾讯混元Turbo S 发布；百度文心4.5或将在3月中旬发布；Anthropic 开放 Claude AI GitHub 集成",
  "highlights": [
    "腾讯混元新一代快思考模型Turbo S 发布,
    "百度文心4.5或将在3月中旬发布",

  ],
  "topics": [
    {{
      "id": 1,
      "description": "腾讯混元新一代快思考模型 Turbo S 发布，即将在腾讯元宝中上线"
    }},
    {{
      "id": 2,
      "description": "百度文心4.5或将在3月中旬发布，提升推理及多模态能力"
    }},
    {{
      "id": 3,
      "description": "Anthropic 开放 Claude AI GitHub 集成，助力开发者代码效率"
    }}
  ],
  "total_topics": 3,
  "source": "AI日报"
}}
==示例结束==

## 限制:
- 所输出的内容必须按照给定的示例回复格式进行组织，不能偏离框架要求。
- 直接返回 JSON 格式的字符串，不要添加额外的说明文字。
"""),
    ("human", "请根据以下输入处理并返回结果：{content}")
])

# 初始化语言模型
llm = ChatOpenAI(
    model="qwq-32b",
    api_key=api_key,
    base_url=base_url,
    temperature=0.7,
    streaming=True
)

# 定义封装函数
def search_and_summarize(input_dict):
    """
    封装函数，接受网页地址和内容的字典，返回符合要求的 JSON 格式结果。
    input_dict: {"url": "网页地址", "content": "网页内容"}
    """
    # 提取 URL 和内容
    content = str(input_dict)
    
    # 使用语言模型生成总结
    # result = llm.invoke(prompt.format(content=content))
    result = llm.stream(prompt.format(content=content))
    for chunk in result:
        print(chunk.content, end='', flush=True)

    return result
    # 解析输出并确保符合 JSON 格式
    # try:
    #     output = json.loads(result)
    #     output["date"] = datetime.now().strftime("%Y-%m-%d")
    #     return output
    # except json.JSONDecodeError:
    #     # 如果输出不是有效 JSON，返回默认格式
    #     return {
    #         "date": datetime.now().strftime("%Y-%m-%d"),
    #         "title": "搜索结果总结",
    #         "highlights": [content],
    #         "topics": [],
    #         "total_topics": 0,
    #     }

# 示例调用
if __name__ == "__main__":
    input_dict = {
        "url": "https://www.aibase.com/zh/daily/16119",
        "content": "2025-03-10 15:23:00AI日报：国家超算平台阿里千问大模型；抖音打击AI炒股诈骗行为；可灵AI上线毛茸茸等三大AI特效\nAI日报：国家超算平台阿里千问大模型；抖音打击AI炒股诈骗行为；可灵AI上线毛茸茸等三大AI特效\n欢迎来到【AI日报】栏目!这里是你每天探索人工智能世界的指南，每天我们为你呈现AI领域的热点内容，聚焦开发者，助你洞悉技术趋势、了解创新AI产品应用。\n新鲜AI产品点击了解:https://top.aibase.com/\n1、警惕!抖音打击AI炒股诈骗行为， AI选股工具、AI炒股课程内容成重灾区\n抖音安全中心近期宣布将加强对股票投资内容的监管，旨在营造健康的网络环境。一些无资质账号利用AI工具发布虚假信息，误导投资者并实施诈骗。抖音已对这些违规账号采取封禁等措施，以保护用户权益。用户在投资时需保持警惕，避免上当受骗。\n【AiBase提要:】\n📉 抖音鼓励财经专业人士分享真实股票信息，抵制谣言。\n🚫 一些无资质账号利用 AI 工具进行荐股，误导投资者。\n🔒 抖音已对违规账号采取封禁等措施，保护用户权益。\n2、国家超算互联网平台接入阿里千问大模型 提供QwQ-32B API\n国家超算互联网平台与阿里巴巴的通义千问大模型达成合作，正式推出千问 QwQ-32B API 服务。该服务为开发者和研究人员提供了免费获取多达100万 tokens 的机会，推动了人工智能技术的发展。千问 QwQ-32B 模型在多个权威评测中表现优异，其能力与 DeepSeek-R1相当，成为 HuggingFace 上最受欢迎的开源大模型之一。\n【AiBase提要:】\n🚀 千问 QwQ-32B API 服务正式上线，用户可免费获取100万 tokens。\n📊 千问 QwQ-32B 模型在评测中表现优异，能力与 DeepSeek-R1相当。\n🌍 阿里通义团队已开源200余款模型，推动人工智能技术发展。\n3、可灵上线FuzzyFuzzy、MochiMochi和BoomBoom三大AI特效 ，创意玩法等你解锁!\n可灵（Kling）推出了其最新版本KLING1.6，正式上线三款AI特效 :FuzzyFuzzy、MochiMochi和BoomBoom。这些特效使用户能够通过简单的操作将静态图片转化为生动的动态视频，极大地丰富了创作的可能性。FuzzyFuzzy以将图片变为毛绒玩具的功能迅速走红，MochiMochi则提供柔软Q弹的视觉体验，而BoomBoom则以其充满能量的动态效果吸引用户。\n【AiBase提要:】\n🎨 FuzzyFuzzy、MochiMochi和BoomBoom三大特效现已上线，用户可通过上传图片体验AI魔法。\n🧸 FuzzyFuzzy能够将图片一键变为可爱的毛绒玩具，操作简单，深受用户喜爱。\n🚀 KLING1.6作为核心技术支持，提供强大的图像到视频生成能力，丰富用户创作可能性。\n4、AI数字人新突破!Hedra推出Character-3模型和Hedra Studio:对图像、文本和音频进行联合推理\nHedra Studio最近推出了Character-3模型，这标志着数字人视频生成技术的重大进步。该模型通过多模态融合技术，能够处理图像、文本和音频，生成高质量的视频内容。用户只需简单上传素材，便可快速生成生动的虚拟角色视频，展现出更高的表现力和情感控制。此外，Hedra Studio旨在降低视频制作门槛，让更多创作者能够轻松制作专业水准的视频，推动创意的实现。\n【AiBase提要:】\n🎥 Character-3模型支持多模态输入，用户可通过上传图像、文本或音频生成虚拟角色视频。\n🌟 新模型具备全身动作捕捉和情感控制功能，提升了视频内容的沉浸感和真实感。\n🛠️ Hedra Studio作为创作平台，致力于降低视频制作门槛，适合各类用户快速生成专业视频。\n5、QQ浏览器推出AI问答功能“元宝快答”\nQQ浏览器于3月7日推出了名为“元宝快答”的AI问答功能，旨在提升用户的搜索体验。该功能基于腾讯混元的“快思考”模型Turbo S，结合搜索增强技术，能够快速检索全网实时信息并提炼重点，为用户提供简洁明了的回答。无论是简单还是复杂的问题，用户都能迅速获得精炼的答案，并可进一步查看原文或进行AI追问，拓展知识边界。\n微信截图_20250310084209.png\n【AiBase提要:】\n💡 采用腾讯混元的“快思考”模型Turbo S，提升搜索效率。\n🔍 元宝快答能够快速检索全网信息，并自动提炼重点。\n📚 用户可查看引用原文或进行AI追问，深入了解问题。\n6、开源版HeyGen来了!\nHeygem是一款专为Windows系统设计的离线视频合成工具，能够精准克隆用户的外貌和声音，确保用户隐私安全。它通过文本和语音驱动虚拟形象，利用先进的AI算法实现高精度的外貌和声音捕捉，支持多语言和自然语言处理。Heygem的用户界面友好，操作简便，适合初学者使用，同时提供安全的创作环境，避免数据泄露。\nimage.png\n【AiBase提要:】\n🌐 Heygem是一款离线视频合成工具，能精准克隆用户外貌和声音。\n🗣️ 通过文本和语音驱动虚拟形象，支持自然语言处理和多语言。\n💻 界面友好，初学者易上手，提供安全隐私保护的创作环境。\n详情链接:https://github.com/GuijiAI/HeyGem.ai\n7、Firecrawl推出LLM.txt API:提供网址即可生成任意网站的LLM.txt\nFirecrawl最近推出了LLMs.txt生成器接口（Alpha版），旨在帮助用户将任何网站的内容转化为适合大语言模型(LLM)训练的文本文件。用户只需提供网站URL，系统便会自动抓取内容并生成llms.txt和llms-full.txt两种格式的文本文件，便于分析和训练。该功能虽然在Alpha阶段，但提供了异步处理和状态监控，用户可设置爬取页面数量及是否生成完整文本。\nimage.png\n【AiBase提要:】\n🌐 用户只需提供网站URL，即可快速生成适用于LLM的文本文件。\n📝 生成两种文本格式，llms.txt为简明总结，llms-full.txt为详细内容，满足不同需求。\n🔒 仅支持公开页面处理，Alpha阶段限制处理网站数量为5000个。\n详情链接:https://docs.firecrawl.dev/features/alpha/llmstxt\n8、AI流量吞噬者:ChatGPT跻身全球十大网站，却几乎不分享流量\n根据Similarweb的数据，ChatGPT在2025年2月的访问量达到了3.9050亿次，尽管环比增长放缓，但同比增长高达137%。ChatGPT在全球网站排名中位列第五，月访问量高达40亿，显示出其强劲的用户基础。然而，尽管用户众多，出站流量却异常稀少，用户点击原始内容的情况罕见，引发业界担忧。\n【AiBase提要:】\n📈 ChatGPT在2025年2月的访问量达到了创纪录的3.9050亿次，同比增长137%。\n🌍 ChatGPT在全球网站排名中位列第五，月访问量高达40亿，占全球网络流量的1.86%。\n⚠️ 尽管用户基数庞大，但出站流量稀少，用户点击原始内容的情况罕见，影响信息验证。\n9、AI界的“火眼金睛”!Finer-CAM让AI理解图像更精准，分类更清晰\nFiner-CAM技术的出现，极大提升了人工智能在图像识别领域的能力，使其能够精准识别细微差别，告别传统方法的模糊与不确定性。通过对比相似类别，Finer-CAM能够锁定独特特征，提供更清晰的解释，帮助用户更好地理解AI的决策过程。这项技术不仅在准确性上超越了传统方法，还实现了多模态零样本学习，展现出强大的应用潜力。\nimage.png\n【AiBase提要:】\n🔍 Finer-CAM通过对比相似类别，精准识别图像中的细微差别，提升了分类的准确性。\n🖼️ 该技术具备强大的降噪功能，能够有效去除背景干扰，让图像解释更加清晰。\n📚 Finer-CAM支持多模态零样本学习，能够理解文字描述并在图像中准确找到对应对象。\n详情链接:https://github.com/Imageomics/Finer-CAM\n10、百度AI创作应用橙篇已正式接入DeepSeek-R1满血版\n3月10日，百度文库旗下的橙篇应用正式接入DeepSeek-R1满血版，标志着其AI辅助功能的显著提升。此次升级使得橙篇能够更高效地满足用户在学习、生活及创作中的多样化需求。用户可以通过智能助手体验到极速且精准的AI服务，极大地提升了学习和生活的效率，成为用户的“第二大脑”。\nimage.png\n【AiBase提要:】\n🚀 橙篇接入DeepSeek-R1后，用户可在App和PC网页版享受高效的AI服务，支持长文生成和深度编辑。\n📚 对于学生，橙篇可快速生成备考计划、论文大纲等，提升学习效率。\n🔍 升级后的橙篇具备深度思考和全网搜索功能，能迅速提供解决方案，帮助用户应对学习和生活中的难题。\n11、推理版局部重绘方法LanPaint，零训练修复图片\nLanPaint 是一款由开发者 scraed 在 GitHub 上发布的图像修复工具，旨在提供高质量的图像修复效果，且无需额外训练。该工具通过多次迭代优化模型的去噪过程，从而实现无缝修复。用户可以简单集成，使用标准的 ComfyUI KSampler 流程，降低了使用门槛。LanPaint 还支持多种复杂的修复任务，展现出强大的图像处理能力。\nimage.png\n【AiBase提要:】\n🎨 零训练修复:支持立即在任何稳定扩散模型上使用，无需额外训练。\n🛠️ 简单集成:与标准 ComfyUI KSampler 相同的工作流程，降低使用门槛。\n🚀 高质量修复:提供高质量、无缝的图像修复效果，支持多种复杂修复任务。\n详情链接:https://github.com/scraed/LanPaint\n12、仅用四周时间!富士康推出中文大语言模型FoxBrain\n富士康旗下的鸿海研究院推出了全新的传统中文大型语言模型FoxBrain，标志着中文人工智能领域的重要进展。该模型在短短四周内完成训练，展现出强大的技术能力，旨在满足市场对中文内容生成和处理的高需求。FoxBrain不仅支持文本生成、翻译和问答等应用场景，还将以开源形式发布，促进AI技术的普及与应用。\n【AiBase提要:】\n🌟 FoxBrain 是富士康鸿海研究院推出的传统中文大型语言模型，训练仅需四周。\n📖 该模型将以开源形式发布，旨在推动中文 AI 技术的发展和普及。\n🔍 FoxBrain 可以应用于文本生成、翻译和问答等多种场景，提升中文内容处理能力。\nAI炒股\nAI选股工具\n抖音\nAI诈骗"
    }
    result = search_and_summarize(input_dict)
    print(json.dumps(result, ensure_ascii=False, indent=2))