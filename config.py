# 系统配置文件
import os
from dotenv import load_dotenv

load_dotenv()

# 尝试导入Streamlit用于Secrets
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# LLM配置 - 优先使用Streamlit Secrets
def get_secret(key, default=""):
    if STREAMLIT_AVAILABLE:
        try:
            return st.secrets.get(key, default)
        except Exception:
            # 本地运行时secrets文件不存在，回退到环境变量
            return os.getenv(key, default)
    return os.getenv(key, default)

# 阿里云DashScope配置
DASHSCOPE_API_KEY = get_secret("DASHSCOPE_API_KEY", "")
MODEL_NAME = get_secret("MODEL_NAME", "qwen-turbo")
MOCK_MODE = get_secret("MOCK_MODE", "false").lower() == "true"

# OpenAI兼容模式配置 - 使用DashScope的兼容接口
OPENAI_API_KEY = DASHSCOPE_API_KEY or get_secret("OPENAI_API_KEY", "")
OPENAI_BASE_URL = get_secret("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = MODEL_NAME or get_secret("LLM_MODEL", "qwen-turbo")

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
