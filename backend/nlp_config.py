# backend/nlp_config.py

# 定义我们关心的政策维度
# 每个维度包含一个"正面"倾向和一个"负面"倾向
POLICY_DIMENSIONS = {
    "monetary_stance": {
        "positive_name": "鹰派 (紧缩)",
        "negative_name": "鸽派 (宽松)",
        "keywords": [
            # 鹰派/紧缩相关的词
            "inflation", "tighten", "hike", "restrictive", "robust", "strong", 
            "concern", "risk", "vigilant", "monitoring", "higher",
            # 鸽派/宽松相关的词
            "employment", "growth", "support", "accommodative", "easing", "cut", 
            "moderate", "softening", "patient", "gradual", "lower"
        ]
    },
    "economic_outlook": {
        "positive_name": "乐观",
        "negative_name": "悲观",
        "keywords": [
            # 乐观相关的词
            "strong", "solid", "rebound", "expansion", "improving", "confident",
            "resilient", "gains", "above", "optimistic",
            # 悲观相关的词
            "weak", "slowing", "uncertainty", "risks", "declined", "soft",
            "below", "headwinds", "challenging", "pessimistic"
        ]
    }
}