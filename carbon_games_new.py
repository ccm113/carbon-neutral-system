import streamlit as st
import random
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class CarbonGames:
    """碳游戏主类"""
    
    def __init__(self):
        # 低碳生活模拟器数据
        self.daily_events = [
            {"time": "早晨", "scenarios": [
                {"question": "起床后，您选择如何洗漱？", "options": [
                    {"text": "🌿 使用冷水洗脸", "emission": 0, "reason": "无需加热水，节省能源"},
                    {"text": "🚿 洗热水澡（5分钟）", "emission": 2, "reason": "短时间热水澡，较节能"},
                    {"text": "🛁 洗热水澡（15分钟）", "emission": 6, "reason": "长时间热水澡消耗较多能源"}
                ]},
                {"question": "早餐选择什么？", "options": [
                    {"text": "🥗 燕麦+水果", "emission": 0.5, "reason": "植物性食物碳排放低"},
                    {"text": "🍳 鸡蛋+面包", "emission": 1.5, "reason": "动物性食物碳排放较高"},
                    {"text": "🍔 汉堡+薯条", "emission": 4, "reason": "加工食品碳足迹高"}
                ]}
            ]},
            {"time": "上午", "scenarios": [
                {"question": "上班/上学选择什么交通工具？", "options": [
                    {"text": "🚲 骑自行车", "emission": 0, "reason": "零碳排放，有益健康"},
                    {"text": "🚌 乘坐公交", "emission": 1, "reason": "公共交通低碳环保"},
                    {"text": "🚗 自驾汽车", "emission": 5, "reason": "私家车碳排放较高"}
                ]},
                {"question": "办公室/教室如何照明？", "options": [
                    {"text": "☀️ 利用自然光", "emission": 0, "reason": "最环保的照明方式"},
                    {"text": "💡 LED灯", "emission": 0.3, "reason": "LED灯节能高效"},
                    {"text": "💡 普通白炽灯", "emission": 1, "reason": "白炽灯能耗高"}
                ]}
            ]},
            {"time": "中午", "scenarios": [
                {"question": "午餐选择什么？", "options": [
                    {"text": "🥦 全素食", "emission": 1, "reason": "植物性饮食碳足迹最低"},
                    {"text": "🍱 荤素搭配", "emission": 3, "reason": "适量肉类较均衡"},
                    {"text": "🥩 大量肉类", "emission": 6, "reason": "肉类生产碳排放高"}
                ]},
                {"question": "餐后饮品选择？", "options": [
                    {"text": "💧 白开水", "emission": 0, "reason": "最环保的饮品"},
                    {"text": "☕ 自带杯子的咖啡", "emission": 0.5, "reason": "减少一次性杯子使用"},
                    {"text": "🥤 瓶装饮料", "emission": 1, "reason": "塑料瓶产生碳排放"}
                ]}
            ]},
            {"time": "下午", "scenarios": [
                {"question": "需要打印文件时？", "options": [
                    {"text": "📄 双面打印", "emission": 0.2, "reason": "节省纸张，减少砍伐"},
                    {"text": "📄 单面打印", "emission": 0.4, "reason": "纸张消耗较多"},
                    {"text": "📄 彩色打印", "emission": 0.8, "reason": "彩色墨盒碳排放更高"}
                ]},
                {"question": "购物时使用什么袋子？", "options": [
                    {"text": "🛍️ 自带环保袋", "emission": 0, "reason": "重复使用，减少塑料"},
                    {"text": "📦 纸袋", "emission": 0.1, "reason": "可降解，但仍有碳排放"},
                    {"text": "🛒 塑料袋", "emission": 0.3, "reason": "塑料污染环境"}
                ]}
            ]},
            {"time": "晚上", "scenarios": [
                {"question": "晚餐后如何处理剩菜？", "options": [
                    {"text": "♻️ 留到明天吃", "emission": 0, "reason": "减少食物浪费"},
                    {"text": "🍽️ 做成新菜肴", "emission": 0.5, "reason": "创意利用剩余食材"},
                    {"text": "🗑️ 直接丢弃", "emission": 2, "reason": "食物浪费产生碳排放"}
                ]},
                {"question": "睡前如何处理电器？", "options": [
                    {"text": "🔌 关闭所有电源", "emission": 0, "reason": "避免待机耗电"},
                    {"text": "⏏️ 拔掉部分插头", "emission": 0.5, "reason": "减少待机能耗"},
                    {"text": "💤 保持待机状态", "emission": 1, "reason": "待机耗电不容忽视"}
                ]}
            ]}
        ]
        
        # 碳循环大挑战数据
        self.carbon_sources = ["化石燃料", "汽车尾气", "工厂排放", "森林砍伐"]
        self.carbon_sinks = ["🌱 植物吸收", "🌊 海洋吸收", "🏜️ 土壤固碳", "🧊 冰川储存"]
        self.sink_capacities = [300, 250, 200, 150]
        
        # 知识问答数据
        self.quiz_questions = [
            {
                "question": "碳中和是指什么？",
                "options": ["碳排放为零", "碳排放量等于碳吸收量", "完全不使用化石燃料"],
                "answer": 1,
                "explanation": "碳中和是指通过植树造林、节能减排等方式，使碳排放量等于碳吸收量。"
            },
            {
                "question": "以下哪种能源是可再生能源？",
                "options": ["煤炭", "天然气", "太阳能"],
                "answer": 2,
                "explanation": "太阳能是可再生能源，取之不尽用之不竭，不会产生碳排放。"
            },
            {
                "question": "一棵树一年大约能吸收多少二氧化碳？",
                "options": ["15公斤", "150公斤", "1500公斤"],
                "answer": 0,
                "explanation": "一棵树一年大约能吸收15-20公斤二氧化碳。"
            },
            {
                "question": "以下哪种出行方式碳排放量最低？",
                "options": ["自驾汽车", "乘坐公交", "骑自行车"],
                "answer": 2,
                "explanation": "骑自行车零碳排放，是最环保的出行方式。"
            },
            {
                "question": "垃圾分类中，电池属于哪一类？",
                "options": ["可回收物", "有害垃圾", "其他垃圾"],
                "answer": 1,
                "explanation": "电池含有有害物质，属于有害垃圾，需要特殊处理。"
            },
            {
                "question": "我国的双碳目标是指？",
                "options": ["碳达峰和碳中和", "低碳和无碳", "节能减排"],
                "answer": 0,
                "explanation": "双碳目标指碳达峰（二氧化碳排放达到峰值后下降）和碳中和。"
            },
            {
                "question": "以下哪种食物碳足迹最高？",
                "options": ["蔬菜", "鸡肉", "牛肉"],
                "answer": 2,
                "explanation": "牛肉生产需要大量土地和饲料，碳足迹远高于蔬菜和鸡肉。"
            },
            {
                "question": "空调温度每升高1°C，能节省多少电量？",
                "options": ["5%", "10%", "20%"],
                "answer": 1,
                "explanation": "空调温度每升高1°C，大约能节省10%的电量。"
            }
        ]

# 游戏1：低碳生活模拟器
def daily_simulator(game):
    st.header("🏠 低碳生活模拟器")
    
    # 初始化状态
    if 'sim_day' not in st.session_state:
        st.session_state.sim_day = 1
        st.session_state.sim_emission = 0
        st.session_state.sim_choices = []
        st.session_state.sim_completed = False
        st.session_state.sim_shown_questions = []  # 记录已显示的问题
    
    day = st.session_state.sim_day
    emission = st.session_state.sim_emission
    choices = st.session_state.sim_choices
    shown_questions = st.session_state.sim_shown_questions
    
    # 丰富的游戏场景数据
    scenarios = [
        {
            "id": "morning_wash",
            "time": "🌅 早晨洗漱",
            "question": "今天早上您如何洗漱？",
            "options": [
                {"text": "🚿 冷水洗澡", "emission": 2, "category": "洗漱"},
                {"text": "🚿 热水洗澡", "emission": 15, "category": "洗漱"},
                {"text": "🧴 冷水洗脸", "emission": 0.5, "category": "洗漱"},
                {"text": "🧴 热水洗脸", "emission": 3, "category": "洗漱"}
            ]
        },
        {
            "id": "breakfast",
            "time": "🍳 早餐时间",
            "question": "今天的早餐您选择？",
            "options": [
                {"text": "🥢 白粥+咸菜", "emission": 1, "category": "饮食"},
                {"text": "🥢 豆浆+油条", "emission": 3, "category": "饮食"},
                {"text": "🥚 鸡蛋+馒头", "emission": 2, "category": "饮食"},
                {"text": "☕ 咖啡+面包", "emission": 5, "category": "饮食"},
                {"text": "🍜 牛肉面", "emission": 6, "category": "饮食"},
                {"text": "🍞 三明治", "emission": 4, "category": "饮食"}
            ]
        },
        {
            "id": "transport",
            "time": "🚶 出行方式",
            "question": "今天上班/上学您选择？",
            "options": [
                {"text": "🚶 步行", "emission": 0, "category": "出行"},
                {"text": "🚲 自行车", "emission": 0.5, "category": "出行"},
                {"text": "🛵 电动车", "emission": 2, "category": "出行"},
                {"text": "🚌 公共交通", "emission": 5, "category": "出行"},
                {"text": "🚗 自驾（燃油车）", "emission": 25, "category": "出行"},
                {"text": "🚗 自驾（新能源车）", "emission": 8, "category": "出行"}
            ]
        },
        {
            "id": "lunch",
            "time": "🍱 午餐选择",
            "question": "今天午餐您选择？",
            "options": [
                {"text": "🥗 自带便当", "emission": 2, "category": "饮食"},
                {"text": "🥢 食堂就餐", "emission": 4, "category": "饮食"},
                {"text": "🍲 外卖（一次性餐具）", "emission": 8, "category": "饮食"},
                {"text": "🍲 外卖（自备餐具）", "emission": 6, "category": "饮食"},
                {"text": "🍔 快餐", "emission": 10, "category": "饮食"},
                {"text": "🥬 素食套餐", "emission": 3, "category": "饮食"}
            ]
        },
        {
            "id": "shopping",
            "time": "🛍️ 购物习惯",
            "question": "购物时您会？",
            "options": [
                {"text": "👜 自带购物袋", "emission": 0, "category": "购物"},
                {"text": "🛍️ 使用商家塑料袋", "emission": 0.5, "category": "购物"},
                {"text": "♻️ 使用可降解塑料袋", "emission": 0.2, "category": "购物"},
                {"text": "📦 选择无包装商品", "emission": 0, "category": "购物"}
            ]
        },
        {
            "id": "leftovers",
            "time": "🥡 剩菜处理",
            "question": "晚餐有剩菜，您会？",
            "options": [
                {"text": "🥡 用保鲜盒装好冷藏（第二天吃）", "emission": 1.5, "category": "饮食"},
                {"text": "🗑️ 直接丢弃", "emission": 3, "category": "饮食"},
                {"text": "🐶 喂宠物", "emission": 0.5, "category": "饮食"},
                {"text": "🌱 做成堆肥", "emission": 0, "category": "饮食"}
            ]
        },
        {
            "id": "evening",
            "time": "🌙 晚间活动",
            "question": "晚上您打算如何度过？",
            "options": [
                {"text": "📚 阅读（开灯）", "emission": 1, "category": "娱乐"},
                {"text": "🎬 看电影（关灯）", "emission": 2, "category": "娱乐"},
                {"text": "🎮 玩游戏（全开灯）", "emission": 4, "category": "娱乐"},
                {"text": "🏃 户外运动", "emission": 0.5, "category": "娱乐"},
                {"text": "💻 工作/学习", "emission": 3, "category": "娱乐"}
            ]
        },
        {
            "id": "appliances",
            "time": "🔌 电器使用",
            "question": "离开房间时您会？",
            "options": [
                {"text": "🔌 关闭所有电器电源", "emission": 0, "category": "用电"},
                {"text": "💡 只关灯，其他待机", "emission": 0.5, "category": "用电"},
                {"text": "🔄 让电器继续运行", "emission": 2, "category": "用电"}
            ]
        }
    ]
    
    # 游戏完成显示结果
    if st.session_state.sim_completed:
        st.subheader("🎉 一天结束！")
        
        # 计算总碳排放量
        total_emission = sum(choice["emission"] for choice in choices)
        
        # 生成称号
        if total_emission <= 15:
            title = "🌟 低碳达人"
            color = "#2ECC71"
            message = "太棒了！你的生活方式非常环保！"
        elif total_emission <= 30:
            title = "🌱 环保卫士"
            color = "#3498DB"
            message = "做得不错！继续保持低碳生活！"
        elif total_emission <= 50:
            title = "😊 低碳新手"
            color = "#F39C12"
            message = "还有改进空间，多关注环保！"
        else:
            title = "🔥 碳足迹大户"
            color = "#E74C3C"
            message = "需要采取更多低碳行动！"
        
        # 计算打败的百分比
        beat_percent = min(99, max(1, 100 - int(total_emission * 1.5)))
        
        # 分析做得好和不好的地方
        good_choices = [c for c in choices if c["emission"] <= 2]
        bad_choices = [c for c in choices if c["emission"] >= 10]
        
        # 显示碳排放量起伏数轴
        st.subheader("📊 全天碳排放量变化")
        times = [c["time"] for c in choices]
        emissions = [c["emission"] for c in choices]
        
        df = pd.DataFrame({"时间": times, "碳排放量(kg)": emissions})
        fig = px.line(df, x="时间", y="碳排放量(kg)", 
                     title="一天中的碳排放量变化",
                     markers=True,
                     color_discrete_sequence=["#10B981"])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示结果
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌍 总碳排放量", f"{total_emission:.1f} kg")
        with col2:
            st.metric("🏆 打败用户", f"{beat_percent}%")
        
        st.markdown(f"<h2 style='color: {color};'>🏅 {title}</h2>", unsafe_allow_html=True)
        st.success(message)
        
        # 分析报告
        st.subheader("📝 今日分析")
        if good_choices:
            st.success("✅ 做得好的地方：")
            for choice in good_choices:
                st.write(f"- {choice['time']}：{choice['text']}")
        
        if bad_choices:
            st.warning("⚠️ 需要改进的地方：")
            for choice in bad_choices:
                st.write(f"- {choice['time']}：{choice['text']}（碳排放较高）")
        
        if not good_choices and not bad_choices:
            st.info("💡 整体表现不错，继续保持！")
        
        # 再玩一次按钮
        if st.button("🔄 再玩一次", use_container_width=True):
            st.session_state.sim_day = 1
            st.session_state.sim_emission = 0
            st.session_state.sim_choices = []
            st.session_state.sim_completed = False
            st.session_state.sim_shown_questions = []
            st.rerun()
        
        return
    
    # 游戏进行中 - 获取下一个未显示的问题
    available_scenarios = [s for s in scenarios if s["id"] not in shown_questions]
    
    if not available_scenarios:
        st.session_state.sim_completed = True
        st.rerun()
    
    # 随机选择一个未显示的问题
    scenario = random.choice(available_scenarios)
    st.session_state.sim_shown_questions.append(scenario["id"])
    
    # 显示问题
    st.subheader(scenario["time"])
    st.write(f"**{scenario['question']}**")
    
    # 选项按钮（不显示碳排放量）
    for option in scenario["options"]:
        if st.button(f"{option['text']}", 
                   key=f"sim_opt_{scenario['id']}_{option['text']}",
                   use_container_width=True):
            st.session_state.sim_choices.append({
                "time": scenario["time"],
                "text": option["text"],
                "emission": option["emission"],
                "category": option["category"]
            })
            st.session_state.sim_emission += option["emission"]
            st.session_state.sim_day += 1
            st.rerun()
    
    # 进度提示
    progress = len(shown_questions) / len(scenarios)
    st.progress(progress)
    st.write(f"⏰ 已完成 {len(shown_questions)}/{len(scenarios)} 个场景")

# 游戏2：碳循环大挑战
def carbon_cycle_challenge(game):
    st.header("🎯 碳循环大挑战")
    
    # 初始化状态
    if 'cycle_score' not in st.session_state:
        st.session_state.cycle_score = 0
        st.session_state.cycle_round = 1
        st.session_state.cycle_co2 = 420
        st.session_state.cycle_sinks = game.sink_capacities.copy()
    
    score = st.session_state.cycle_score
    round_num = st.session_state.cycle_round
    co2_level = st.session_state.cycle_co2
    sink_levels = st.session_state.cycle_sinks
    
    # 游戏结束
    if round_num > 10 or co2_level >= 500:
        st.subheader("🏁 游戏结束")
        if co2_level < 350:
            st.success(f"🎉 恭喜！成功将CO₂降至 {co2_level} ppm！")
            st.balloons()
        else:
            st.warning(f"😔 挑战失败！最终CO₂浓度为 {co2_level} ppm")
        
        st.metric("最终得分", score)
        
        if st.button("🔄 再玩一次", key="cycle_restart"):
            st.session_state.cycle_score = 0
            st.session_state.cycle_round = 1
            st.session_state.cycle_co2 = 420
            st.session_state.cycle_sinks = game.sink_capacities.copy()
            st.rerun()
        return
    
    # 游戏状态
    st.subheader(f"第 {round_num}/10 回合")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("大气CO₂浓度", f"{co2_level} ppm", delta=f"目标: <350 ppm", delta_color="inverse")
    with col2:
        st.metric("当前得分", score)
    
    # CO₂进度条
    progress = min(co2_level / 500, 1)
    st.progress(progress)
    
    # 碳汇选择
    st.subheader("🌿 选择碳汇吸收CO₂")
    cols = st.columns(2)
    
    for i, (sink, capacity) in enumerate(zip(game.carbon_sinks, sink_levels)):
        with cols[i % 2]:
            if st.button(f"{sink}\n\n剩余容量: {capacity} kg", key=f"cycle_sink_{i}_{round_num}", use_container_width=True):
                absorb = min(capacity, random.randint(20, 50))
                st.session_state.cycle_co2 -= absorb
                st.session_state.cycle_sinks[i] -= absorb
                st.session_state.cycle_score += absorb
                st.session_state.cycle_round += 1
                st.success(f"✅ {sink}吸收了 {absorb} kg CO₂！")
                st.rerun()
    
    # 随机事件
    if random.random() < 0.3:
        event_type = random.choice(["工厂排放", "森林火灾", "火山爆发"])
        emission = random.randint(30, 60)
        st.session_state.cycle_co2 += emission
        st.error(f"⚠️ 随机事件：{event_type}！CO₂增加 {emission} kg")
        time.sleep(1)
        st.rerun()
    
    st.info(f"💡 提示：大气中CO₂安全水平是350 ppm，当前是 {co2_level} ppm")

# 游戏3：环保知识问答
def eco_quiz(game):
    st.header("📚 环保知识问答王")
    
    # 初始化状态
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_asked = []
        st.session_state.quiz_show_answer = False
    
    score = st.session_state.quiz_score
    index = st.session_state.quiz_index
    asked = st.session_state.quiz_asked
    
    # 游戏结束
    if len(asked) >= len(game.quiz_questions):
        st.subheader("🏆 问答结束！")
        
        percentage = (score / len(game.quiz_questions)) * 100
        
        if percentage >= 80:
            rating = "🌟 环保学霸"
            color = "#FFD700"
        elif percentage >= 60:
            rating = "🌱 环保达人"
            color = "#2ECC71"
        elif percentage >= 40:
            rating = "📚 环保学习者"
            color = "#3498DB"
        else:
            rating = "💪 继续加油"
            color = "#F39C12"
        
        st.markdown(f"<h2 style='color: {color};'>{rating}</h2>", unsafe_allow_html=True)
        st.metric("最终得分", f"{score}/{len(game.quiz_questions)}")
        st.progress(percentage / 100)
        
        if st.button("🔄 再玩一次", key="quiz_restart"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_index = 0
            st.session_state.quiz_asked = []
            st.session_state.quiz_show_answer = False
            st.rerun()
        return
    
    # 获取下一个问题
    available = [i for i in range(len(game.quiz_questions)) if i not in asked]
    current_idx = random.choice(available)
    question = game.quiz_questions[current_idx]
    
    st.subheader(f"📝 第 {len(asked) + 1}/{len(game.quiz_questions)} 题")
    st.write(f"**{question['question']}**")
    
    # 选项按钮
    if not st.session_state.quiz_show_answer:
        for i, option in enumerate(question["options"]):
            if st.button(f"{i+1}. {option}", key=f"quiz_option_{current_idx}_{i}", use_container_width=True):
                st.session_state.quiz_asked.append(current_idx)
                st.session_state.quiz_show_answer = True
                
                if i == question["answer"]:
                    st.success("✅ 回答正确！")
                    st.session_state.quiz_score += 1
                else:
                    st.error(f"❌ 回答错误！正确答案是 {question['options'][question['answer']]}")
                st.rerun()
    else:
        # 显示答案和解释
        st.info(f"💡 {question['explanation']}")
        
        if st.button("➡️ 下一题", key="quiz_next"):
            st.session_state.quiz_show_answer = False
            st.rerun()
    
    st.progress(len(asked) / len(game.quiz_questions))

# 游戏4：碳中和农场
def carbon_farm():
    st.header("🌾 碳中和农场")
    
    # 初始化状态
    if 'farm_money' not in st.session_state:
        st.session_state.farm_money = 100
        st.session_state.farm_trees = 0
        st.session_state.farm_solar = 0
        st.session_state.farm_plants = 0
        st.session_state.farm_day = 1
        st.session_state.farm_co2 = 0
    
    money = st.session_state.farm_money
    trees = st.session_state.farm_trees
    solar = st.session_state.farm_solar
    plants = st.session_state.farm_plants
    day = st.session_state.farm_day
    total_co2 = st.session_state.farm_co2
    
    # 农场状态
    st.subheader(f"📅 第 {day} 天")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 金币", money)
    with col2:
        st.metric("🌲 树木", trees)
    with col3:
        st.metric("☀️ 太阳能板", solar)
    with col4:
        st.metric("🌱 植物", plants)
    
    # 碳平衡计算
    co2_produced = day * 10  # 每天产生的碳排放
    co2_absorbed = trees * 15 + plants * 5 + solar * 20
    balance = co2_absorbed - co2_produced
    
    st.subheader("📊 碳平衡")
    st.metric("累计碳排放", f"{co2_produced} kg")
    st.metric("累计碳吸收", f"{co2_absorbed} kg")
    st.metric("碳平衡", f"{balance} kg", delta="目标: ≥0", delta_color="normal" if balance >= 0 else "inverse")
    
    # 商店
    st.subheader("🛒 商店")
    items = [
        {"name": "🌲 树苗", "price": 20, "effect": "trees", "description": "每棵树每年吸收15kg CO₂"},
        {"name": "☀️ 太阳能板", "price": 50, "effect": "solar", "description": "每天发电减少20kg CO₂"},
        {"name": "🌱 蔬菜种子", "price": 10, "effect": "plants", "description": "每株植物吸收5kg CO₂"}
    ]
    
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i]:
            if st.button(f"{item['name']}\n\n💰 {item['price']}\n\n{item['description']}", 
                       key=f"farm_item_{i}", use_container_width=True,
                       disabled=money < item['price']):
                if money >= item['price']:
                    st.session_state.farm_money -= item['price']
                    st.session_state[f"farm_{item['effect']}"] += 1
                    st.success(f"✅ 购买了 {item['name']}！")
                    st.rerun()
    
    # 收获
    if st.button("🌾 收获农产品", key="farm_harvest"):
        harvest = plants * 5
        st.session_state.farm_money += harvest
        st.success(f"✅ 收获了 ¥{harvest}！")
        st.rerun()
    
    # 下一天
    if st.button("➡️ 进入下一天", key="farm_next_day"):
        st.session_state.farm_day += 1
        st.session_state.farm_co2 += 10  # 每天基础碳排放
        st.rerun()
    
    # 游戏目标
    st.info("🎯 目标：通过种植树木和使用可再生能源，实现碳中和！")

# 游戏菜单
def show_games_page():
    """显示游戏主页面"""
    game = CarbonGames()
    
    st.title("🎮 碳游戏乐园")
    st.markdown("---")
    
    # 游戏选择卡
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 低碳生活模拟器")
        st.write("模拟一天的生活，做出环保选择！")
        if st.button("🎮 开始游戏", key="btn_sim", use_container_width=True):
            st.session_state['game_mode'] = 'simulator'
            st.rerun()
    
    with col1:
        st.subheader("🎯 碳循环大挑战")
        st.write("在限定时间内将CO₂降至安全水平！")
        if st.button("🎮 开始挑战", key="btn_cycle", use_container_width=True):
            st.session_state['game_mode'] = 'cycle'
            st.rerun()
    
    with col2:
        st.subheader("📚 环保知识问答王")
        st.write("测试你的环保知识储备！")
        if st.button("🎮 开始答题", key="btn_quiz", use_container_width=True):
            st.session_state['game_mode'] = 'quiz'
            st.rerun()
    
    with col2:
        st.subheader("🌾 碳中和农场")
        st.write("经营农场，实现碳中和！")
        if st.button("🎮 开始经营", key="btn_farm", use_container_width=True):
            st.session_state['game_mode'] = 'farm'
            st.rerun()
    
    # 返回按钮
    if st.session_state.get('game_mode'):
        if st.button("← 返回主菜单", key="back_to_menu"):
            st.session_state['game_mode'] = None
            # 清除所有游戏状态
            keys_to_clear = ['sim_day', 'sim_score', 'sim_emission', 'sim_choices', 'sim_events',
                            'cycle_score', 'cycle_round', 'cycle_co2', 'cycle_sinks',
                            'quiz_score', 'quiz_index', 'quiz_asked', 'quiz_show_answer',
                            'farm_money', 'farm_trees', 'farm_solar', 'farm_plants', 'farm_day', 'farm_co2']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # 游戏内容
    if st.session_state.get('game_mode') == 'simulator':
        daily_simulator(game)
    elif st.session_state.get('game_mode') == 'cycle':
        carbon_cycle_challenge(game)
    elif st.session_state.get('game_mode') == 'quiz':
        eco_quiz(game)
    elif st.session_state.get('game_mode') == 'farm':
        carbon_farm()

if __name__ == "__main__":
    show_games_page()