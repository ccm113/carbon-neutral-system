# 系统配置文件
import os
from dotenv import load_dotenv

load_dotenv()

# LLM配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

# 碳排放系数配置（单位：kg CO2）
CARBON_FACTORS = {
    "electricity": 0.581,  # 每度电碳排放系数
    "gasoline": 2.32,      # 每升汽油碳排放系数
    "diesel": 2.63,        # 每升柴油碳排放系数
    "natural_gas": 2.16,   # 每立方米天然气碳排放系数
}

# 分类权重
SCORE_WEIGHTS = {
    "garbage": 0.3,    # 垃圾分类权重
    "electricity": 0.4, # 用电权重
    "transport": 0.3,  # 出行权重
}

# 测试用户账户
TEST_USERS = {
    "user1": "password1",
    "user2": "password2",
    "admin": "admin123"
}
