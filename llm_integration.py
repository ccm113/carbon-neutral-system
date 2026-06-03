import os
import json
from typing import Optional
from config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

# 尝试导入OpenAI库，如果失败则使用模拟模式
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 常用家电功率参考表（单位：W）
APPLIANCE_POWER = {
    '空调': {'低挡': 800, '中挡': 1200, '高挡': 1800, '默认': 1200},
    '热水器': {'低挡': 800, '中挡': 1500, '高挡': 2000, '默认': 1500},
    '洗衣机': {'低挡': 200, '中挡': 300, '高挡': 500, '默认': 300},
    '冰箱': {'低挡': 50, '中挡': 80, '高挡': 120, '默认': 80},
    '电视': {'低挡': 50, '中挡': 80, '高挡': 120, '默认': 80},
    '电脑': {'低挡': 60, '中挡': 100, '高挡': 150, '默认': 100},
    '照明': {'低挡': 5, '中挡': 10, '高挡': 20, '默认': 10},
    '电饭煲': {'低挡': 500, '中挡': 800, '高挡': 1000, '默认': 800},
    '微波炉': {'低挡': 500, '中挡': 700, '高挡': 1000, '默认': 700},
    '电磁炉': {'低挡': 800, '中挡': 1200, '高挡': 2000, '默认': 1200},
}

# 挡位系数
GEAR_COEFFICIENT = {'低挡': 0.7, '中挡': 1.0, '高挡': 1.5, '节能': 0.5, '静音': 0.6}

class LLMIntegration:
    def __init__(self):
        self.client = None
        self._init_client()
        self.conversation_history = []  # 对话历史，用于上下文理解
    
    def _init_client(self):
        """初始化LLM客户端"""
        if OPENAI_API_KEY and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    base_url=OPENAI_BASE_URL
                )
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def is_available(self):
        """检查LLM是否可用"""
        return self.client is not None
    
    def generate_content(self, prompt, system_prompt=None):
        """生成内容（通用接口）"""
        if not self.is_available():
            # LLM不可用时返回错误标记，让调用方处理
            return "llm_unavailable"
        
        result = self._call_llm(prompt, system_prompt)
        # 如果返回错误标记，设置client为None，下次调用会走模拟数据
        if result in ["api_key_error", "api_quota_error", "api_unknown_error", "llm_unavailable"]:
            self.client = None
            return "llm_unavailable"
        return result
    
    def generate_carbon_reduction_suggestions(self, user_profile):
        """根据用户画像生成个性化减碳建议（支持垃圾分类数据可选）"""
        if not self.is_available():
            return self._generate_simulated_suggestions(user_profile)
        
        # 构建用户数据描述（只包含有数据的项）
        data_lines = []
        data_lines.append(f"- 综合评分：{user_profile['total_score']:.1f}分")
        data_lines.append(f"- 低碳等级：{user_profile['level']['level']}")
        
        if user_profile.get('has_garbage') and user_profile['garbage_score'] is not None:
            data_lines.append(f"- 垃圾分类得分：{user_profile['garbage_score']}分")
        else:
            data_lines.append(f"- 垃圾分类：未提供数据")
        
        if user_profile.get('has_electricity') and user_profile['electricity_score'] is not None:
            data_lines.append(f"- 用电习惯得分：{user_profile['electricity_score']}分")
        else:
            data_lines.append(f"- 用电习惯：未提供数据")
        
        if user_profile.get('has_transport') and user_profile['transport_score'] is not None:
            data_lines.append(f"- 出行方式得分：{user_profile['transport_score']}分")
        else:
            data_lines.append(f"- 出行方式：未提供数据")
        
        data_lines.append(f"- 总碳排放量：{user_profile['stats']['total_carbon']:.1f} kg CO2")
        
        prompt = f"""
        你是一位专业的低碳生活顾问，请根据以下用户画像数据，生成个性化、拟人化的减碳建议：

        用户画像数据：
        {chr(10).join(data_lines)}

        碳排放短板：
        {json.dumps(user_profile['weaknesses'], ensure_ascii=False, indent=2)}

        要求：
        1. 语气亲切友好，使用第一人称，像朋友聊天一样给出建议
        2. 针对用户的具体短板给出针对性建议
        3. 建议要具体可行，不要太笼统
        4. 分点列出，但不要使用markdown格式，用自然语言连接
        5. 语言简洁，每条建议不超过两句话

        请生成3-5条个性化减碳建议。
        """
        
        result = self._call_llm(prompt)
        # 如果API调用失败，回退到模拟数据
        if result in ["api_key_error", "api_quota_error", "api_unknown_error", "llm_unavailable"]:
            self.client = None
            return self._generate_simulated_suggestions(user_profile)
        return result
    
    def generate_analysis_report(self, user_profile):
        """生成个人低碳生活分析报告（包含减碳建议）"""
        if not self.is_available():
            return self._generate_simulated_report(user_profile)
        
        prompt = f"""
        你是一位专业的低碳生活分析师，请根据以下用户数据，撰写一份详细的个人低碳生活分析报告：

        用户画像数据：
        - 综合评分：{user_profile['total_score']}分
        - 低碳等级：{user_profile['level']['level']}
        - 垃圾分类得分：{user_profile['garbage_score']}分
        - 用电习惯得分：{user_profile['electricity_score']}分
        - 出行方式得分：{user_profile['transport_score']}分
        - 总碳排放量：{user_profile['stats']['total_carbon']:.1f} kg CO2

        统计数据：
        垃圾分类：
        - 总投放次数：{user_profile['stats']['garbage'].get('total_count', 0)}次
        - 正确分类次数：{user_profile['stats']['garbage'].get('correct_count', 0)}次
        - 正确率：{user_profile['stats']['garbage'].get('accuracy_rate', 0) * 100:.1f}%

        用电情况：
        - 总用电量：{user_profile['stats']['electricity'].get('total_consumption', 0):.1f} kWh
        - 日均用电：{user_profile['stats']['electricity'].get('avg_daily', 0):.1f} kWh
        - 用电碳排放：{user_profile['stats']['electricity'].get('carbon_emission', 0):.1f} kg CO2

        出行情况：
        - 总出行次数：{user_profile['stats']['transport'].get('total_trips', 0)}次
        - 总出行距离：{user_profile['stats']['transport'].get('total_distance', 0):.1f} km
        - 绿色出行比例：{user_profile['stats']['transport'].get('green_ratio', 0) * 100:.1f}%
        - 出行碳排放：{user_profile['stats']['transport'].get('carbon_emission', 0):.1f} kg CO2

        碳排放短板：
        {json.dumps(user_profile['weaknesses'], ensure_ascii=False, indent=2)}

        要求：
        1. 报告结构清晰，包含以下部分：
           - 标题：个人低碳生活分析报告
           - 概述：总体评价和碳足迹概况
           - 分项分析：用电习惯分析、出行方式分析、垃圾分类分析
           - 碳排放短板：重点改进领域
           - 个性化减碳建议：3-5条具体可行的建议，语气亲切友好
           - 总结与展望
        2. 语言专业但易懂，避免使用过于技术化的术语
        3. 数据可视化描述要具体
        4. 建议要实用可行，针对用户的具体短板给出针对性建议
        5. 整体风格正式但不生硬，减碳建议部分可以更亲切一些

        请生成一份完整的个人低碳生活分析报告。
        """
        
        result = self._call_llm(prompt)
        # 如果API调用失败，回退到模拟数据
        if result in ["api_key_error", "api_quota_error", "api_unknown_error", "llm_unavailable"]:
            self.client = None
            return self._generate_simulated_report(user_profile)
        return result
    
    def answer_question(self, question, user_profile=None):
        """回答用户关于低碳、垃圾分类、节电出行的问题（支持意图识别和上下文理解）"""
        # 将当前问题添加到对话历史
        self.conversation_history.append({"role": "user", "content": question})
        
        if not self.is_available():
            return self._answer_simulated(question, user_profile)
        
        # 使用意图识别回答问题
        try:
            return self._answer_with_intent_recognition(question, user_profile)
        except Exception as e:
            print(f"意图识别失败，回退到普通回答: {e}")
            # 回退到普通LLM回答
            profile_context = self._build_profile_context(user_profile)
            history_context = self._build_history_context()
            
            prompt = f"""
            你是一位专业的低碳生活知识顾问，正在与用户进行对话。
            
            【分析数据概览】
            {profile_context}

            【对话历史】
            {history_context}

            【当前问题】
            {question}

            要求：
            1. 必须结合用户的数据分析结果进行回答，直接引用数据
            2. 参考对话历史，理解上下文
            3. 回答务必简洁，不超过3句话
        4. 语言通俗易懂，不要冗长
        5. 如果涉及垃圾分类，参考中国的垃圾分类标准

        请给出简短、直接的回答。
        """
        
        response = self._call_llm(prompt)
        
        # 如果API调用失败，回退到模拟数据
        if response in ["api_key_error", "api_quota_error", "api_unknown_error", "llm_unavailable"]:
            self.client = None
            simulated_response = self._answer_simulated(question, user_profile)
            self.conversation_history.append({"role": "assistant", "content": simulated_response})
            return simulated_response
        
        # 将回复添加到对话历史
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _build_profile_context(self, user_profile):
        """构建完整的用户画像上下文"""
        if not user_profile:
            return "用户尚未加载数据进行分析。"
        
        context = []
        
        # 综合信息
        context.append(f"- 综合评分：{user_profile['total_score']:.1f}分")
        context.append(f"- 低碳职级：{user_profile['level']['level']}")
        context.append(f"- 总碳排放量：{user_profile['stats']['total_carbon']:.1f} kg CO2")
        
        # 分项得分
        if user_profile.get('has_garbage') and user_profile['garbage_score'] is not None:
            context.append(f"- 垃圾分类得分：{user_profile['garbage_score']}分")
            stats = user_profile['stats'].get('garbage', {})
            if stats.get('total_count'):
                context.append(f"  - 投放次数：{stats['total_count']}次，正确率：{stats.get('accuracy_rate', 0)*100:.1f}%")
        else:
            context.append(f"- 垃圾分类：未提供数据")
        
        if user_profile.get('has_electricity') and user_profile['electricity_score'] is not None:
            context.append(f"- 用电习惯得分：{user_profile['electricity_score']}分")
            stats = user_profile['stats'].get('electricity', {})
            if stats.get('total_consumption'):
                context.append(f"  - 总用电量：{stats['total_consumption']:.1f}kWh，日均：{stats.get('avg_daily', 0):.1f}kWh")
            # 添加时段分布数据
            time_stats = stats.get('time_stats')
            if time_stats is not None and len(time_stats) > 0:
                time_list = []
                for period, consumption in time_stats.items():
                    time_list.append(f"{period}: {consumption:.1f}kWh")
                context.append(f"  - 时段用电分布：{', '.join(time_list)}")
            # 添加设备分布数据
            device_stats = stats.get('device_stats')
            if device_stats is not None and len(device_stats) > 0:
                device_list = []
                for device, consumption in device_stats.items():
                    device_list.append(f"{device}: {consumption:.1f}kWh")
                context.append(f"  - 设备用电分布：{', '.join(device_list)}")
        else:
            context.append(f"- 用电习惯：未提供数据")
        
        if user_profile.get('has_transport') and user_profile['transport_score'] is not None:
            context.append(f"- 出行方式得分：{user_profile['transport_score']}分")
            stats = user_profile['stats'].get('transport', {})
            if stats.get('total_trips'):
                context.append(f"  - 出行次数：{stats['total_trips']}次，绿色出行比例：{stats.get('green_ratio', 0)*100:.1f}%")
            # 添加出行方式分布数据
            mode_stats = stats.get('mode_stats')
            if mode_stats is not None and len(mode_stats) > 0:
                mode_list = []
                for mode, row in mode_stats.iterrows():
                    mode_list.append(f"{mode}: {row['出行次数']}次")
                context.append(f"  - 出行方式分布：{', '.join(mode_list)}")
        else:
            context.append(f"- 出行方式：未提供数据")
        
        # 短板分析
        if user_profile.get('weaknesses'):
            context.append("\n【碳排放短板】")
            for w in user_profile['weaknesses']:
                context.append(f"- {w['category']}：{w['level']}（得分：{w['score']}分），建议：{w['suggestion']}")
        else:
            context.append("\n【碳排放短板】：暂无明显短板")
        
        return "\n".join(context)
    
    def _build_history_context(self):
        """构建对话历史上下文（最近5轮）"""
        if not self.conversation_history:
            return "这是对话的开始。"
        
        # 只保留最近5轮对话
        recent_history = self.conversation_history[-10:]  # 5问5答
        
        history_lines = []
        for i, msg in enumerate(recent_history):
            role = "用户" if msg['role'] == 'user' else "助手"
            history_lines.append(f"{role}：{msg['content']}")
        
        return "\n".join(history_lines)
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
    
    def _call_llm(self, prompt, system_prompt=None):
        """调用LLM生成回复"""
        try:
            system_msg = system_prompt or "你是一位专业的低碳生活顾问，擅长为用户提供个性化的减碳建议和环保知识解答。"
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM API error: {e}")
            error_str = str(e).lower()
            # 隐藏敏感信息，提供友好提示
            if "invalid_api_key" in error_str or "incorrect_api_key" in error_str or "401" in str(e):
                # API密钥无效，标记服务不可用，后续使用模拟数据
                self.client = None
                return "api_key_error"
            elif "rate_limit" in error_str or "quota" in error_str:
                return "api_quota_error"
            else:
                return "api_unknown_error"
    
    def _parse_intent(self, question):
        """使用LLM进行意图识别"""
        system_prompt = """
        你是一个意图识别专家。请分析用户的问题，并输出JSON格式的结果。
        
        可能的意图类型：
        - data_query: 查询用户数据（如分数、排名、统计数据等）
        - suggestion: 寻求建议或指导
        - knowledge: 询问知识或概念解释
        - chat: 闲聊或其他
        
        如果是data_query，请同时识别查询的数据类型：
        - general: 综合信息（综合评分、等级、碳排放量）
        - electricity: 用电数据（用电得分、日均用电、设备用电、时段用电、月度用电）
        - transport: 出行数据（出行得分、次数、距离、绿色出行比例、出行方式）
        - garbage: 垃圾分类数据（得分、正确率、投放次数）
        - weakness: 短板分析
        
        输出格式：{"intent": "意图类型", "data_type": "数据类型或null", "query_detail": "查询的具体内容"}
        """
        
        prompt = f"分析用户问题并识别意图：{question}"
        
        try:
            response = self._call_llm(prompt, system_prompt)
            result = json.loads(response)
            return result
        except Exception as e:
            print(f"意图识别失败: {e}")
            return {"intent": "chat", "data_type": None, "query_detail": question}
    
    def _get_data_answer(self, intent_result, user_profile):
        """根据意图识别结果从用户数据中提取答案"""
        if intent_result['intent'] != 'data_query' or not user_profile:
            return None
        
        data_type = intent_result['data_type']
        query_detail = intent_result['query_detail']
        
        # 根据数据类型构建答案
        if data_type == 'general':
            if '评分' in query_detail or '总分' in query_detail:
                return f"您的综合评分为{user_profile['total_score']:.1f}分。"
            elif '等级' in query_detail or '职级' in query_detail:
                return f"您的低碳职级是「{user_profile['level']['level']}」。"
            elif '碳排放' in query_detail or '碳足迹' in query_detail:
                return f"您的总碳排放量为{user_profile['stats']['total_carbon']:.1f}kg CO2。"
        
        elif data_type == 'electricity':
            stats = user_profile['stats'].get('electricity', {})
            if '得分' in query_detail:
                return f"您的用电习惯得分为{user_profile['electricity_score']}分。"
            elif '日均' in query_detail:
                return f"您的日均用电量为{stats.get('avg_daily', 0):.1f}kWh。"
            elif '总用电' in query_detail:
                return f"您的总用电量为{stats.get('total_consumption', 0):.1f}kWh。"
            elif '电器' in query_detail or '设备' in query_detail:
                device_stats = stats.get('device_stats')
                if device_stats is not None and len(device_stats) > 0:
                    if '最低' in query_detail:
                        min_device = min(device_stats.items(), key=lambda x: x[1])
                        return f"用电量最低的电器是{min_device[0]}，为{min_device[1]:.1f}kWh。"
                    else:
                        max_device = max(device_stats.items(), key=lambda x: x[1])
                        return f"用电量最高的电器是{max_device[0]}，为{max_device[1]:.1f}kWh。"
                return "您的数据中没有设备用电明细。"
            elif '时段' in query_detail:
                time_stats = stats.get('time_stats')
                if time_stats is not None and len(time_stats) > 0:
                    if '最低' in query_detail:
                        min_time = min(time_stats.items(), key=lambda x: x[1])
                        return f"{min_time[0]}时段用电量最低，为{min_time[1]:.1f}kWh。"
                    else:
                        max_time = max(time_stats.items(), key=lambda x: x[1])
                        return f"{max_time[0]}时段用电量最高，为{max_time[1]:.1f}kWh。"
                return "您的数据中没有时段用电明细。"
            elif '月' in query_detail:
                monthly_trend = stats.get('monthly_trend')
                if monthly_trend is not None and len(monthly_trend) > 0:
                    if '最低' in query_detail:
                        min_month = monthly_trend.idxmin()
                        return f"{min_month}用电量最低，为{monthly_trend.min():.1f}kWh。"
                    else:
                        max_month = monthly_trend.idxmax()
                        return f"{max_month}用电量最高，为{monthly_trend.max():.1f}kWh。"
                return "您的数据中没有月度用电明细。"
        
        elif data_type == 'transport':
            stats = user_profile['stats'].get('transport', {})
            if '得分' in query_detail:
                return f"您的出行方式得分为{user_profile['transport_score']}分。"
            elif '次数' in query_detail:
                return f"您的总出行次数为{stats.get('total_trips', 0)}次。"
            elif '距离' in query_detail:
                return f"您的总出行距离为{stats.get('total_distance', 0):.1f}公里。"
            elif '绿色' in query_detail:
                return f"您的绿色出行比例为{stats.get('green_ratio', 0)*100:.1f}%。"
            elif '方式' in query_detail or '工具' in query_detail:
                mode_stats = stats.get('mode_stats')
                if mode_stats is not None and len(mode_stats) > 0:
                    max_mode = mode_stats['出行次数'].idxmax()
                    return f"最常选择的出行方式是{max_mode}，共{mode_stats['出行次数'].max()}次。"
                return "您的数据中没有出行方式明细。"
        
        elif data_type == 'garbage':
            stats = user_profile['stats'].get('garbage', {})
            if '得分' in query_detail:
                return f"您的垃圾分类得分为{user_profile['garbage_score']}分。"
            elif '正确率' in query_detail:
                return f"您的垃圾分类正确率为{stats.get('accuracy_rate', 0)*100:.1f}%。"
            elif '次数' in query_detail:
                return f"您的垃圾投放总次数为{stats.get('total_count', 0)}次。"
            elif '哪种' in query_detail or '哪种垃圾' in query_detail or '最多' in query_detail:
                type_stats = stats.get('type_stats')
                if type_stats is not None and len(type_stats) > 0:
                    max_type = type_stats['count'].idxmax()
                    max_count = type_stats['count'].max()
                    return f"您投放最多的垃圾类型是{max_type}，共{max_count}次。"
                return "您的数据中没有垃圾类型明细。"
        
        elif data_type == 'weakness':
            weaknesses = user_profile.get('weaknesses', [])
            if weaknesses:
                weakness_list = [w['category'] for w in weaknesses]
                return f"建议关注：{', '.join(weakness_list)}。"
            return "您各方面都做得不错，继续保持！"
        
        return None
    
    def _answer_with_intent_recognition(self, question, user_profile=None, conversation_history=None):
        """使用意图识别回答用户问题"""
        # 1. 意图识别
        intent_result = self._parse_intent(question)
        
        # 2. 如果是数据查询，先尝试从数据中提取答案
        if intent_result['intent'] == 'data_query' and user_profile:
            data_answer = self._get_data_answer(intent_result, user_profile)
            if data_answer:
                return data_answer
        
        # 3. 否则使用普通LLM回答
        context = ""
        if user_profile:
            context = self._build_user_context(user_profile)
        
        history_context = self._build_history_context()
        
        prompt = f"""
        【对话历史】
        {history_context}
        
        【用户数据】
        {context}
        
        【当前问题】
        {question}
        
        请根据以上信息回答用户问题，回答要简短（不超过3句话），优先使用用户数据。
        """
        
        return self._call_llm(prompt)
    
    def _generate_simulated_suggestions(self, user_profile):
        """生成模拟的减碳建议（当LLM不可用时，支持可选数据）"""
        suggestions = []
        
        # 根据垃圾分类得分（只在有数据时检查）
        if user_profile.get('has_garbage') and user_profile['garbage_score'] is not None:
            if user_profile['garbage_score'] < 60:
                suggestions.append("垃圾分类方面还有提升空间呢！建议您投放前先看一下分类指南，可回收物记得清洗干净再投放哦。")
        
        # 根据用电得分（只在有数据时检查）
        if user_profile.get('has_electricity') and user_profile['electricity_score'] is not None:
            if user_profile['electricity_score'] < 60:
                suggestions.append("用电习惯可以优化一下！夏天空调设置在26℃左右最省电，记得随手关闭不用的电器电源。")
        
        # 根据出行得分（只在有数据时检查）
        if user_profile.get('has_transport') and user_profile['transport_score'] is not None:
            if user_profile['transport_score'] < 60:
                suggestions.append("出行方式可以更绿色一些！短途出行试试步行或骑行，既环保又能锻炼身体。")
        
        # 通用建议
        if len(suggestions) < 3:
            suggestions.append("建议您每天记录自己的低碳行为，积少成多，慢慢养成好习惯。")
        
        if len(suggestions) < 4:
            suggestions.append("可以尝试每周设定一个低碳日，当天尽量减少碳排放，挑战一下自己！")
        
        if len(suggestions) < 5:
            suggestions.append("和家人朋友一起参与低碳行动，互相监督，效果会更好哦！")
        
        return "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))
    
    def _generate_simulated_report(self, user_profile):
        """生成模拟的分析报告（当LLM不可用时，支持可选数据）"""
        p = user_profile
        stats = p['stats']
        
        report = f"""
个人低碳生活分析报告
========================

【报告概述】
尊敬的用户，您好！根据您的数据，我们为您生成了这份低碳生活分析报告。

【综合评估】
您的综合得分为 {p['total_score']:.1f} 分，属于「{p['level']['level']}」。
{p['level']['description']}

【分项分析】
"""
        
        # 垃圾分类分析（可选）
        if p.get('has_garbage'):
            report += """
一、垃圾分类分析
----------------
- 总投放次数：{stats['garbage'].get('total_count', 0)} 次
- 正确分类次数：{stats['garbage'].get('correct_count', 0)} 次
- 正确率：{stats['garbage'].get('accuracy_rate', 0) * 100:.1f}%

评估：您的垃圾分类正确率处于{'较高' if stats['garbage'].get('accuracy_rate', 0) > 0.7 else '一般' if stats['garbage'].get('accuracy_rate', 0) > 0.5 else '较低'}水平。
""".format(stats=stats)
        else:
            report += """
一、垃圾分类分析
----------------
- 未提供数据

评估：此项数据未提供，建议您如果有相关数据可以上传进行分析。
"""
        
        # 用电习惯分析（可选）
        if p.get('has_electricity'):
            report += """
二、用电习惯分析
----------------
- 总用电量：{stats['electricity'].get('total_consumption', 0):.1f} kWh
- 日均用电：{stats['electricity'].get('avg_daily', 0):.1f} kWh
- 用电碳排放：{stats['electricity'].get('carbon_emission', 0):.1f} kg CO2

评估：您的日均用电量{'低于' if stats['electricity'].get('avg_daily', 0) < 10 else '接近' if stats['electricity'].get('avg_daily', 0) < 15 else '高于'}普通家庭平均水平。
""".format(stats=stats)
        else:
            report += """
二、用电习惯分析
----------------
- 未提供数据

评估：此项数据未提供，建议您如果有相关数据可以上传进行分析。
"""
        
        # 出行方式分析（可选）
        if p.get('has_transport'):
            report += """
三、出行方式分析
----------------
- 总出行次数：{stats['transport'].get('total_trips', 0)} 次
- 总出行距离：{stats['transport'].get('total_distance', 0):.1f} km
- 绿色出行比例：{stats['transport'].get('green_ratio', 0) * 100:.1f}%
- 出行碳排放：{stats['transport'].get('carbon_emission', 0):.1f} kg CO2

评估：您的绿色出行比例{'较高' if stats['transport'].get('green_ratio', 0) > 0.6 else '一般' if stats['transport'].get('green_ratio', 0) > 0.4 else '较低'}。
""".format(stats=stats)
        else:
            report += """
三、出行方式分析
----------------
- 未提供数据

评估：此项数据未提供，建议您如果有相关数据可以上传进行分析。
"""
        
        report += """
【碳排放短板】
"""
        if p['weaknesses']:
            for w in p['weaknesses']:
                report += f"- {w['category']}：{w['level']}（{w['score']}分）\n"
        else:
            report += "暂无明显短板，继续保持！\n"
        
        report += f"""
【改进建议】
1. {'加强垃圾分类学习，提高分类准确率。' if p['garbage_score'] < 60 else '继续保持良好的垃圾分类习惯。'}
2. {'优化用电习惯，减少不必要的能源消耗。' if p['electricity_score'] < 60 else '继续保持节约用电的好习惯。'}
3. {'增加绿色出行比例，减少私家车使用。' if p['transport_score'] < 60 else '继续保持绿色出行的好习惯。'}

【总结】
您的总碳排放量为 {stats['total_carbon']:.1f} kg CO2。继续努力，您可以成为更好的低碳生活践行者！

---
报告生成时间：系统自动生成
"""
        
        return report.strip()
    
    def _answer_simulated(self, question, user_profile=None):
        """模拟回答用户问题（当LLM不可用时，支持结合用户画像）"""
        question_lower = question.lower()
        
        # === 统一数据查询引擎 ===
        # 首先尝试精确数据查询
        data_answer = self._query_user_data(question_lower, user_profile)
        if data_answer:
            return data_answer
        
        # === 通用知识问答 ===
        # 垃圾分类相关
        if '垃圾' in question_lower or '分类' in question_lower:
            if user_profile and user_profile.get('has_garbage'):
                return f"您的垃圾分类得分为{user_profile['garbage_score']}分。中国垃圾分四类：可回收物、有害垃圾、厨余垃圾、其他垃圾。"
            return "中国垃圾分四类：可回收物、有害垃圾、厨余垃圾、其他垃圾。"
        
        # 家电电量计算服务
        elif '计算' in question_lower or '耗电' in question_lower:
            result = self._calculate_appliance_power(question_lower)
            if result:
                return result
        
        # 节电相关
        elif '电' in question_lower or '节能' in question_lower or '省电' in question_lower:
            if user_profile and user_profile.get('has_electricity'):
                return f"您的用电得分为{user_profile['electricity_score']}分。省电建议：空调设26℃，随手关灯，拔掉待机插头。"
            return "省电小贴士：空调设26℃，随手关灯，拔掉待机插头。"
        
        # 出行相关
        elif '出行' in question_lower or '交通' in question_lower or '绿色出行' in question_lower:
            if user_profile and user_profile.get('has_transport'):
                green_ratio = user_profile['stats']['transport'].get('green_ratio', 0) * 100
                return f"您的出行得分为{user_profile['transport_score']}分，绿色出行比例{green_ratio:.1f}%。建议短途步行或骑行。"
            return "绿色出行推荐：步行、骑行、公共交通。"
        
        # 通用回答
        if user_profile:
            return f"您的综合评分为{user_profile['total_score']:.1f}分。请问您想了解哪方面的内容？"
        return "请问您想了解垃圾分类、用电节能还是出行方式相关的内容？"
    
    def _query_user_data(self, question_lower, user_profile):
        """统一数据查询引擎 - 处理所有类型的用户数据查询"""
        if not user_profile:
            return None
        
        # 定义数据查询规则
        queries = [
            # (关键词组合, 数据类型, 字段, 处理函数)
            # 综合信息
            (('综合评分',), 'general', 'total_score', lambda v: f"您的综合评分为{v:.1f}分。"),
            (('总分',), 'general', 'total_score', lambda v: f"您的综合评分为{v:.1f}分。"),
            (('等级', '职级'), 'general', 'level', lambda v: f"您的低碳职级是「{v['level']}」。"),
            (('碳排放量',), 'general', 'total_carbon', lambda v: f"您的总碳排放量为{v:.1f}kg CO2。"),
            (('碳足迹',), 'general', 'total_carbon', lambda v: f"您的碳足迹为{v:.1f}kg CO2。"),
            
            # 用电数据
            (('用电得分',), 'electricity', 'electricity_score', lambda v: f"您的用电习惯得分为{v}分。"),
            (('日均用电',), 'electricity', 'avg_daily', lambda v: f"您的日均用电量为{v:.1f}kWh。"),
            (('总用电量',), 'electricity', 'total_consumption', lambda v: f"您的总用电量为{v:.1f}kWh。"),
            (('用电量最高', '电器'), 'electricity', 'device_stats', self._format_top_device),
            (('用电最高', '电器'), 'electricity', 'device_stats', self._format_top_device),
            (('耗电最多',), 'electricity', 'device_stats', self._format_top_device),
            (('时段', '用电'), 'electricity', 'time_stats', self._format_top_period),
            (('哪个时段',), 'electricity', 'time_stats', self._format_top_period),
            (('哪个月', '用电'), 'electricity', 'monthly_trend', self._format_top_month),
            (('月份', '用电'), 'electricity', 'monthly_trend', self._format_top_month),
            
            # 出行数据
            (('出行得分',), 'transport', 'transport_score', lambda v: f"您的出行方式得分为{v}分。"),
            (('出行次数',), 'transport', 'total_trips', lambda v: f"您的总出行次数为{v}次。"),
            (('出行距离',), 'transport', 'total_distance', lambda v: f"您的总出行距离为{v:.1f}公里。"),
            (('绿色出行', '比例'), 'transport', 'green_ratio', lambda v: f"您的绿色出行比例为{v*100:.1f}%。"),
            (('出行方式', '最多'), 'transport', 'mode_stats', self._format_top_mode),
            (('交通工具', '最多'), 'transport', 'mode_stats', self._format_top_mode),
            (('最常', '出行'), 'transport', 'mode_stats', self._format_top_mode),
            
            # 垃圾分类数据
            (('垃圾分类', '得分'), 'garbage', 'garbage_score', lambda v: f"您的垃圾分类得分为{v}分。"),
            (('垃圾分类', '正确率'), 'garbage', 'accuracy_rate', lambda v: f"您的垃圾分类正确率为{v*100:.1f}%。"),
            (('投放次数',), 'garbage', 'total_count', lambda v: f"您的垃圾总投放次数为{v}次。"),
            (('哪种垃圾',), 'garbage', 'type_stats', self._format_top_garbage_type),
            (('垃圾最多',), 'garbage', 'type_stats', self._format_top_garbage_type),
            
            # 短板分析
            (('改进',), 'general', 'weaknesses', self._format_weaknesses),
            (('短板',), 'general', 'weaknesses', self._format_weaknesses),
            (('需要改',), 'general', 'weaknesses', self._format_weaknesses),
        ]
        
        # 尝试匹配查询
        for keywords, data_type, field, formatter in queries:
            # 检查是否所有关键词都在问题中
            if all(keyword in question_lower for keyword in keywords):
                # 获取数据
                value = self._get_data_value(data_type, field, user_profile)
                if value is not None:
                    return formatter(value)
                else:
                    return f"您的数据中没有{keywords[0]}相关明细。"
        
        return None
    
    def _get_data_value(self, data_type, field, user_profile):
        """从用户画像中获取指定的数据值"""
        if data_type == 'general':
            if field == 'total_score':
                return user_profile.get('total_score')
            elif field == 'level':
                return user_profile.get('level')
            elif field == 'total_carbon':
                return user_profile['stats'].get('total_carbon')
            elif field == 'weaknesses':
                return user_profile.get('weaknesses', [])
        
        elif data_type == 'electricity':
            if not user_profile.get('has_electricity'):
                return None
            stats = user_profile['stats'].get('electricity', {})
            if field == 'electricity_score':
                return user_profile.get('electricity_score')
            elif field == 'avg_daily':
                return stats.get('avg_daily')
            elif field == 'total_consumption':
                return stats.get('total_consumption')
            elif field == 'device_stats':
                return stats.get('device_stats')
            elif field == 'time_stats':
                return stats.get('time_stats')
            elif field == 'monthly_trend':
                return stats.get('monthly_trend')
        
        elif data_type == 'transport':
            if not user_profile.get('has_transport'):
                return None
            stats = user_profile['stats'].get('transport', {})
            if field == 'transport_score':
                return user_profile.get('transport_score')
            elif field == 'total_trips':
                return stats.get('total_trips')
            elif field == 'total_distance':
                return stats.get('total_distance')
            elif field == 'green_ratio':
                return stats.get('green_ratio')
            elif field == 'mode_stats':
                return stats.get('mode_stats')
        
        elif data_type == 'garbage':
            if not user_profile.get('has_garbage'):
                return None
            stats = user_profile['stats'].get('garbage', {})
            if field == 'garbage_score':
                return user_profile.get('garbage_score')
            elif field == 'accuracy_rate':
                return stats.get('accuracy_rate')
            elif field == 'total_count':
                return stats.get('total_count')
            elif field == 'type_stats':
                return stats.get('type_stats')
        
        return None
    
    def _format_top_device(self, device_stats):
        """格式化用电设备最高的数据"""
        if device_stats is None or len(device_stats) == 0:
            return "您的数据中没有各电器的分项用电明细。"
        max_device = max(device_stats.items(), key=lambda x: x[1])
        total = device_stats.sum()
        percentage = (max_device[1] / total) * 100
        return f"根据您的数据，用电量最高的电器是{max_device[0]}，占比{percentage:.1f}%。"
    
    def _format_top_period(self, time_stats):
        """格式化用电时段最高的数据"""
        if time_stats is None or len(time_stats) == 0:
            return "您的数据中没有分时段用电明细。"
        max_time = max(time_stats.items(), key=lambda x: x[1])
        total = time_stats.sum()
        percentage = (max_time[1] / total) * 100
        return f"根据您的数据，{max_time[0]}时段用电量最高，占比{percentage:.1f}%。"
    
    def _format_top_month(self, monthly_stats, query_type='max'):
        """格式化月度用电量数据（支持最高/最低）"""
        if monthly_stats is None or len(monthly_stats) == 0:
            return "您的数据中没有月度用电明细。"
        if query_type == 'min':
            max_month = monthly_stats.idxmin()
            max_value = monthly_stats.min()
            return f"根据您的数据，{max_month}用电量最低，为{max_value:.1f}kWh。"
        else:
            max_month = monthly_stats.idxmax()
            max_value = monthly_stats.max()
            return f"根据您的数据，{max_month}用电量最高，为{max_value:.1f}kWh。"
    
    def _format_top_mode(self, mode_stats):
        """格式化出行方式最多的数据"""
        if mode_stats is None or len(mode_stats) == 0:
            return "您的数据中没有出行方式明细。"
        max_mode = mode_stats['出行次数'].idxmax()
        max_count = mode_stats['出行次数'].max()
        total = mode_stats['出行次数'].sum()
        percentage = (max_count / total) * 100
        return f"根据您的数据，最常选择的出行方式是{max_mode}，共{max_count}次，占比{percentage:.1f}%。"
    
    def _format_weaknesses(self, weaknesses):
        """格式化短板分析数据"""
        if not weaknesses:
            return "您各方面都做得不错，继续保持！"
        weakness_list = [w['category'] for w in weaknesses]
        return f"建议关注：{', '.join(weakness_list)}。"
    
    def _format_top_garbage_type(self, type_stats):
        """格式化投放最多的垃圾类型"""
        if type_stats is None or len(type_stats) == 0:
            return "您的数据中没有垃圾类型明细。"
        max_type = type_stats['count'].idxmax()
        max_count = type_stats['count'].max()
        return f"您投放最多的垃圾类型是{max_type}，共{max_count}次。"
    
    def _calculate_appliance_power(self, question):
        """家电电量计算服务：根据家电类型、使用时间、功率、挡位计算用电量"""
        # 提取家电类型
        appliance = None
        for app in APPLIANCE_POWER.keys():
            if app in question:
                appliance = app
                break
        
        if not appliance:
            return None
        
        # 提取使用时间（单位：小时）
        hours = self._extract_time(question)
        
        # 提取功率（单位：W）
        power = self._extract_power(question, appliance)
        
        # 提取挡位
        gear = self._extract_gear(question)
        
        # 如果没有提取到时间，询问用户
        if hours is None:
            return f"请告诉我{appliance}使用了多长时间（例如：2小时30分钟），我帮您计算用电量。"
        
        # 如果没有提取到功率，使用默认功率
        if power is None:
            power = APPLIANCE_POWER[appliance]['默认']
        
        # 应用挡位系数
        if gear:
            coeff = GEAR_COEFFICIENT.get(gear, 1.0)
            power = int(power * coeff)
        
        # 计算用电量：用电量(kWh) = 功率(W) × 时间(h) ÷ 1000
        kwh = (power * hours) / 1000
        
        # 计算碳排放量：碳排放(kg CO2) = 用电量(kWh) × 0.581
        carbon = kwh * 0.581
        
        # 计算费用（假设电价0.6元/kWh）
        cost = kwh * 0.6
        
        result = f"""
        {appliance}用电计算结果：
        - 功率：{power}W{'（{gear}模式）' if gear else ''}
        - 使用时间：{hours:.1f}小时
        - 用电量：{kwh:.2f} kWh（度）
        - 碳排放量：{carbon:.2f} kg CO2
        - 预计电费：{cost:.2f} 元
        
        计算公式：用电量 = 功率(W) × 时间(h) ÷ 1000
        """
        
        return result.strip()
    
    def _extract_time(self, question):
        """从问题中提取时间（单位：小时）"""
        import re
        
        # 匹配 "X小时Y分钟" 格式
        match = re.search(r'(\d+)\s*小时\s*(\d+)\s*分钟', question)
        if match:
            hours = int(match.group(1)) + int(match.group(2)) / 60
            return hours
        
        # 匹配 "X小时" 格式
        match = re.search(r'(\d+(?:\.\d+)?)\s*小时', question)
        if match:
            return float(match.group(1))
        
        # 匹配 "X分钟" 格式
        match = re.search(r'(\d+)\s*分钟', question)
        if match:
            return int(match.group(1)) / 60
        
        # 匹配 "X天" 格式（按24小时计算）
        match = re.search(r'(\d+)\s*天', question)
        if match:
            return int(match.group(1)) * 24
        
        return None
    
    def _extract_power(self, question):
        """从问题中提取功率（单位：W）"""
        import re
        
        # 匹配 "X瓦" 或 "XW" 格式
        match = re.search(r'(\d+)\s*[瓦W]', question)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_gear(self, question):
        """从问题中提取挡位"""
        for gear in GEAR_COEFFICIENT.keys():
            if gear in question:
                return gear
        return None
