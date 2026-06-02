import streamlit as st
import plotly.graph_objects as go
import random
import time

class CarbonGame:
    """碳循环游戏组件"""
    
    def __init__(self):
        # 碳循环节点数据
        self.nodes = {
            "atmosphere": {"name": "大气CO₂", "color": "#87CEEB", "pos": [0.5, 0.9]},
            "plants": {"name": "植被", "color": "#228B22", "pos": [0.3, 0.6]},
            "soil": {"name": "土壤", "color": "#CD853F", "pos": [0.5, 0.4]},
            "ocean": {"name": "海洋", "color": "#1E90FF", "pos": [0.7, 0.6]},
            "fossil": {"name": "化石燃料", "color": "#8B4513", "pos": [0.2, 0.2]},
            "waste": {"name": "废弃物", "color": "#696969", "pos": [0.8, 0.2]}
        }
        
        # 正确的碳流向
        self.correct_flows = [
            ("atmosphere", "plants", "光合作用", 250),
            ("plants", "atmosphere", "呼吸作用", 150),
            ("plants", "soil", "落叶腐殖", 100),
            ("atmosphere", "ocean", "海洋溶解", 220),
            ("ocean", "atmosphere", "海洋释放", 200),
            ("soil", "atmosphere", "微生物分解", 50),
            ("fossil", "atmosphere", "燃烧排放", 350),
            ("waste", "atmosphere", "焚烧处理", 60),
            ("waste", "soil", "资源化利用", 40)
        ]
        
        # 行动卡片
        self.action_cards = [
            {"id": "tree", "name": "🌳 植树造林", "effect": -15, "cost": 10, "desc": "种植树木吸收CO₂"},
            {"id": "solar", "name": "☀️ 太阳能", "effect": -50, "cost": 30, "desc": "使用太阳能发电"},
            {"id": "bike", "name": "🚲 绿色出行", "effect": -20, "cost": 5, "desc": "选择骑行或公交"},
            {"id": "recycle", "name": "♻️ 垃圾分类", "effect": -10, "cost": 3, "desc": "做好垃圾分类"},
            {"id": "energy", "name": "💡 节能改造", "effect": -30, "cost": 20, "desc": "更换节能设备"},
            {"id": "factory", "name": "🏭 减排工厂", "effect": -100, "cost": 80, "desc": "工厂减排改造"}
        ]
        
        # 碳足迹场景
        self.footprint_scenarios = [
            {
                "question": "今天你打算怎么出行？",
                "options": [
                    {"text": "🚗 自驾上班", "emission": 20, "reason": "私家车排放较高"},
                    {"text": "🚌 乘坐公交", "emission": 2, "reason": "公共交通更低碳"},
                    {"text": "🚲 骑自行车", "emission": 0, "reason": "零碳排放，还能锻炼身体"}
                ]
            },
            {
                "question": "中午吃什么？",
                "options": [
                    {"text": "🍔 外卖快餐", "emission": 5, "reason": "包装和运输增加碳排放"},
                    {"text": "🍳 自带便当", "emission": 2, "reason": "减少包装浪费"},
                    {"text": "🥗 素食沙拉", "emission": 1, "reason": "植物性食物碳排放更低"}
                ]
            },
            {
                "question": "购物选择？",
                "options": [
                    {"text": "🛒 超市购物", "emission": 3, "reason": "商品运输产生排放"},
                    {"text": "🧺 农贸市场", "emission": 1, "reason": "本地食材更环保"},
                    {"text": "🏠 线上网购", "emission": 5, "reason": "快递运输碳排放"}
                ]
            },
            {
                "question": "晚上照明？",
                "options": [
                    {"text": "💡 开所有灯", "emission": 2, "reason": "浪费电能"},
                    {"text": "💡 只开需要的灯", "emission": 1, "reason": "合理用电"},
                    {"text": "🕯️ 使用LED灯", "emission": 0.3, "reason": "LED更节能"}
                ]
            },
            {
                "question": "周末活动？",
                "options": [
                    {"text": "🏕️ 郊外自驾游", "emission": 50, "reason": "长途驾驶碳排放高"},
                    {"text": "🏃 公园跑步", "emission": 0, "reason": "零碳运动"},
                    {"text": "🎬 在家看电影", "emission": 3, "reason": "相对低碳"}
                ]
            }
        ]

def show_game_menu():
    """游戏主菜单"""
    st.header("🎮 碳循环游戏")
    st.markdown("---")
    
    # 游戏介绍
    with st.expander("📖 游戏说明", expanded=True):
        st.markdown("""
        欢迎来到碳循环游戏！这里有三个有趣的小游戏，帮助您了解碳循环知识和低碳生活方式。
        
        **🧩 碳循环拼图**：通过连接节点学习碳在自然界的循环路径
        
        **🌡️ 碳中和挑战**：扮演地球管理者，通过策略选择降低大气CO₂浓度
        
        **👣 碳足迹测试**：测试您的日常生活方式，了解个人碳足迹
        
        选择一个游戏开始吧！
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🧩 碳循环拼图")
        st.image("https://neeko-copilot.bytedance.net/api/text_to_image?prompt=carbon%20cycle%20puzzle%20game%20educational%20green%20environment&image_size=square", use_container_width=True)
        st.write("拖拽连接碳循环节点，学习碳的流动路径")
        if st.button("开始游戏", key="puzzle_btn"):
            st.session_state['game_mode'] = 'puzzle'
            st.session_state['puzzle_flows'] = []
            st.rerun()
    
    with col2:
        st.subheader("🌡️ 碳中和挑战")
        st.image("https://neeko-copilot.bytedance.net/api/text_to_image?prompt=climate%20action%20game%20carbon%20neutral%20earth%20saving&image_size=square", use_container_width=True)
        st.write("通过选择行动卡片，将大气CO₂降至安全水平")
        if st.button("开始挑战", key="challenge_btn"):
            st.session_state['game_mode'] = 'challenge'
            st.session_state['co2_level'] = 420
            st.session_state['score'] = 0
            st.session_state['round'] = 1
            st.session_state['budget'] = 100
            st.rerun()
    
    with col3:
        st.subheader("👣 碳足迹测试")
        st.image("https://neeko-copilot.bytedance.net/api/text_to_image?prompt=carbon%20footprint%20quiz%20eco%20friendly%20choices&image_size=square", use_container_width=True)
        st.write("测试你的生活方式碳足迹，了解环保选择")
        if st.button("开始测试", key="footprint_btn"):
            st.session_state['game_mode'] = 'footprint'
            st.session_state['footprint_score'] = 0
            st.session_state['footprint_step'] = 0
            st.session_state['footprint_choices'] = []
            st.rerun()

def reset_puzzle_state():
    """重置拼图游戏状态"""
    keys_to_clear = ['puzzle_flows']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def show_puzzle_game():
    """碳循环拼图游戏"""
    game = CarbonGame()
    
    st.header("🧩 碳循环拼图")
    st.markdown("---")
    
    # 游戏规则说明
    with st.expander("📋 游戏规则", expanded=True):
        st.markdown("""
        **游戏目标**：正确连接所有碳循环节点，理解碳在自然界中的流动路径。
        
        **游戏规则**：
        1. 选择一个起始节点（碳的来源）
        2. 选择一个目标节点（碳的去向）
        3. 点击"添加连接"按钮建立连接
        4. 正确的连接会显示绿色，错误的连接会显示红色
        5. 尝试连接所有正确的碳流向
        
        **碳循环节点说明**：
        - 🌤️ **大气CO₂**：大气中的二氧化碳
        - 🌱 **植被**：通过光合作用吸收CO₂
        - 🌍 **土壤**：储存植物落叶腐殖质中的碳
        - 🌊 **海洋**：溶解和储存大量CO₂
        - ⛏️ **化石燃料**：地下储存的煤炭、石油、天然气
        - ♻️ **废弃物**：人类活动产生的垃圾
        
        **提示**：碳在大气、植被、土壤、海洋之间循环流动，人类活动会影响这个循环。
        """)
    
    # 初始化游戏状态
    if 'puzzle_flows' not in st.session_state:
        st.session_state['puzzle_flows'] = []
    
    # 节点选择
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("选择起始节点")
        source_node = st.selectbox("从哪个节点出发？", list(game.nodes.keys()), 
                                   format_func=lambda x: game.nodes[x]["name"],
                                   key="puzzle_source")
    
    with col2:
        st.subheader("选择目标节点")
        target_node = st.selectbox("连接到哪个节点？", 
                                   [k for k in game.nodes.keys() if k != source_node],
                                   format_func=lambda x: game.nodes[x]["name"],
                                   key="puzzle_target")
    
    # 添加连接
    if st.button("🔗 添加连接", key="puzzle_add"):
        if source_node != target_node:
            new_flow = (source_node, target_node)
            if new_flow not in st.session_state['puzzle_flows']:
                st.session_state['puzzle_flows'].append(new_flow)
                st.success(f"已连接 {game.nodes[source_node]['name']} → {game.nodes[target_node]['name']}")
            else:
                st.warning("这个连接已经存在")
    
    # 清除连接
    if st.button("🗑️ 清除所有连接", key="puzzle_clear"):
        st.session_state['puzzle_flows'] = []
        st.rerun()
    
    st.divider()
    
    # 可视化连接
    st.subheader("碳循环图")
    
    # 创建节点坐标
    node_x = [game.nodes[k]["pos"][0] for k in game.nodes.keys()]
    node_y = [game.nodes[k]["pos"][1] for k in game.nodes.keys()]
    node_labels = [game.nodes[k]["name"] for k in game.nodes.keys()]
    node_colors = [game.nodes[k]["color"] for k in game.nodes.keys()]
    
    # 创建连接线
    link_source = []
    link_target = []
    link_colors = []
    
    node_order = list(game.nodes.keys())
    
    for flow in st.session_state['puzzle_flows']:
        source_idx = node_order.index(flow[0])
        target_idx = node_order.index(flow[1])
        link_source.append(source_idx)
        link_target.append(target_idx)
        
        # 检查是否正确
        is_correct = any(f[0] == flow[0] and f[1] == flow[1] for f in game.correct_flows)
        link_colors.append("rgba(39, 174, 96, 0.6)" if is_correct else "rgba(231, 76, 60, 0.6)")
    
    fig = go.Figure(data=[go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(color=node_colors, size=20),
        text=node_labels,
        textposition='bottom center',
        hoverinfo='text'
    )])
    
    # 添加连接线
    for i in range(len(link_source)):
        fig.add_trace(go.Scatter(
            x=[node_x[link_source[i]], node_x[link_target[i]]],
            y=[node_y[link_source[i]], node_y[link_target[i]]],
            mode='lines',
            line=dict(color=link_colors[i], width=3),
            hoverinfo='none'
        ))
    
    fig.update_layout(
        width=600,
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示进度
    correct_count = sum(1 for flow in st.session_state['puzzle_flows'] 
                       if any(f[0] == flow[0] and f[1] == flow[1] for f in game.correct_flows))
    total_correct = len(game.correct_flows)
    
    st.progress(correct_count / total_correct)
    st.write(f"✅ 正确连接: {correct_count}/{total_correct}")
    
    # 显示正确答案按钮
    if st.button("👀 查看答案", key="puzzle_answer"):
        st.subheader("正确的碳流向：")
        for flow in game.correct_flows:
            st.write(f"• **{game.nodes[flow[0]]['name']}** → **{game.nodes[flow[1]]['name']}** ({flow[2]})")
    
    # 返回按钮
    if st.button("← 返回菜单", key="puzzle_back"):
        reset_puzzle_state()
        st.session_state['game_mode'] = None
        st.rerun()

def reset_challenge_state():
    """重置挑战游戏状态"""
    keys_to_clear = ['co2_level', 'score', 'round', 'budget']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def show_challenge_game():
    """碳中和挑战游戏"""
    game = CarbonGame()
    
    st.header("🌡️ 碳中和挑战")
    st.markdown("---")
    
    # 游戏规则说明
    with st.expander("📋 游戏规则", expanded=True):
        st.markdown("""
        **游戏目标**：在20回合内将大气CO₂浓度从420 ppm降至350 ppm以下，实现碳中和！
        
        **游戏规则**：
        1. 每回合选择一张行动卡片来减少CO₂
        2. 每张卡片有不同的减排效果和成本
        3. 您初始有¥100预算，需要合理分配
        4. 在20回合内将CO₂降至350 ppm以下即可获胜
        
        **行动卡片说明**：
        - 🌳 植树造林：花费¥10，减少15kg CO₂
        - ☀️ 太阳能：花费¥30，减少50kg CO₂
        - 🚲 绿色出行：花费¥5，减少20kg CO₂
        - ♻️ 垃圾分类：花费¥3，减少10kg CO₂
        - 💡 节能改造：花费¥20，减少30kg CO₂
        - 🏭 减排工厂：花费¥80，减少100kg CO₂
        
        **提示**：合理规划预算，优先选择性价比高的减排措施！
        """)
    
    # 初始化游戏状态
    if 'co2_level' not in st.session_state:
        st.session_state['co2_level'] = 420
        st.session_state['score'] = 0
        st.session_state['round'] = 1
        st.session_state['budget'] = 100
    
    co2 = st.session_state['co2_level']
    score = st.session_state['score']
    round_num = st.session_state['round']
    budget = st.session_state['budget']
    
    # 游戏状态显示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("大气CO₂", f"{co2} ppm", 
                  delta="安全水平: 350 ppm", delta_color="inverse")
    
    with col2:
        st.metric("当前回合", f"{round_num}/20")
    
    with col3:
        st.metric("可用预算", f"¥{budget}")
    
    with col4:
        st.metric("累计得分", score)
    
    # CO₂进度条
    st.progress(min(co2 / 500, 1))
    
    # 游戏结束判断
    if round_num > 20:
        st.subheader("🏁 游戏结束")
        if co2 <= 350:
            st.success(f"🎉 恭喜！你成功将CO₂降至 {co2} ppm，实现碳中和！")
            st.balloons()
        else:
            st.warning(f"😔 挑战失败！最终CO₂浓度为 {co2} ppm，距离目标还差 {co2 - 350} ppm")
        
        st.write(f"🏆 最终得分: {score}")
        
        if st.button("🔄 再玩一次", key="challenge_restart"):
            reset_challenge_state()
            st.session_state['game_mode'] = None
            st.rerun()
        
        return
    
    # 行动卡片选择
    st.subheader("🃏 选择行动卡片")
    cols = st.columns(3)
    
    for i, card in enumerate(game.action_cards):
        with cols[i % 3]:
            disabled = card["cost"] > budget
            
            if st.button(f"**{card['name']}**\n\n效果: {card['effect']}kg CO₂\n花费: ¥{card['cost']}",
                       key=f"challenge_card_{card['id']}",
                       disabled=disabled,
                       use_container_width=True):
                
                if not disabled:
                    st.session_state['co2_level'] += card['effect']
                    st.session_state['score'] += abs(card['effect'])
                    st.session_state['budget'] -= card['cost']
                    st.session_state['round'] += 1
                    st.success(f"✅ 使用了 {card['name']}，CO₂减少了 {abs(card['effect'])} kg！")
                    st.rerun()
    
    # 提示信息
    st.info(f"💡 提示：第 {round_num} 回合，你需要将CO₂降至350 ppm以下才能获胜！")
    
    # 返回按钮
    if st.button("← 返回菜单", key="challenge_back"):
        reset_challenge_state()
        st.session_state['game_mode'] = None
        st.rerun()

def reset_footprint_state():
    """重置碳足迹测试状态"""
    keys_to_clear = ['footprint_step', 'footprint_score', 'footprint_choices']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def show_footprint_game():
    """碳足迹测试游戏"""
    game = CarbonGame()
    
    st.header("👣 碳足迹测试")
    st.markdown("---")
    
    # 游戏规则说明
    with st.expander("📋 测试说明", expanded=True):
        st.markdown("""
        **测试目的**：了解您的日常生活方式对环境的影响，计算您的个人碳足迹。
        
        **测试规则**：
        1. 回答5个关于日常生活选择的问题
        2. 每个选择对应不同的碳排放量
        3. 测试结束后显示您的碳足迹评级和改进建议
        
        **碳足迹评级标准**：
        - 🌟 低碳达人（≤10kg/天）：生活方式非常环保
        - 🌱 环保爱好者（11-20kg/天）：做得不错，还有改进空间
        - 🌿 低碳学习者（21-35kg/天）：需要关注环保
        - 🔥 碳足迹较高（>35kg/天）：建议采取更多低碳行动
        
        **提示**：选择更环保的选项可以减少您的碳足迹！
        """)
    
    # 初始化游戏状态
    if 'footprint_step' not in st.session_state:
        st.session_state['footprint_step'] = 0
        st.session_state['footprint_score'] = 0
        st.session_state['footprint_choices'] = []
    
    step = st.session_state['footprint_step']
    total_score = st.session_state['footprint_score']
    choices = st.session_state['footprint_choices']
    
    # 游戏结束
    if step >= len(game.footprint_scenarios):
        st.subheader("📊 测试结果")
        
        # 计算评级
        if total_score <= 10:
            rating = "🌟 低碳达人"
            color = "#27AE60"
            advice = "太棒了！你的生活方式非常环保，继续保持！"
        elif total_score <= 20:
            rating = "🌱 环保爱好者"
            color = "#3498DB"
            advice = "做得不错！还有一些地方可以改进，比如减少自驾出行。"
        elif total_score <= 35:
            rating = "🌿 低碳学习者"
            color = "#F39C12"
            advice = "还有提升空间！建议多选择公共交通和素食。"
        else:
            rating = "🔥 碳足迹较高"
            color = "#E74C3C"
            advice = "需要关注环保！从小事做起，逐步减少碳排放。"
        
        st.markdown(f"<h2 style='color: {color};'>{rating}</h2>", unsafe_allow_html=True)
        st.metric("总碳足迹", f"{total_score} kg CO₂/天")
        
        st.subheader("你的选择回顾：")
        for i, (scenario, choice) in enumerate(zip(game.footprint_scenarios, choices)):
            st.write(f"{i+1}. **{scenario['question']}**")
            st.write(f"   你的选择: {choice['text']} ({choice['emission']} kg CO₂)")
        
        st.info(advice)
        
        if st.button("🔄 重新测试", key="footprint_restart"):
            reset_footprint_state()
            st.session_state['game_mode'] = None
            st.rerun()
        
        return
    
    # 当前问题
    scenario = game.footprint_scenarios[step]
    
    st.subheader(f"📝 问题 {step + 1}/{len(game.footprint_scenarios)}")
    st.write(f"**{scenario['question']}**")
    
    # 选项按钮
    for idx, option in enumerate(scenario['options']):
        if st.button(f"{option['text']}\n\n💬 {option['reason']}",
                   key=f"footprint_option_{step}_{idx}",
                   use_container_width=True):
            
            st.session_state['footprint_score'] += option['emission']
            st.session_state['footprint_choices'].append(option)
            st.session_state['footprint_step'] += 1
            st.rerun()

def show_carbon_game_page():
    """显示碳循环游戏页面"""
    # 检查游戏模式
    if 'game_mode' not in st.session_state or st.session_state['game_mode'] is None:
        show_game_menu()
    elif st.session_state['game_mode'] == 'puzzle':
        show_puzzle_game()
    elif st.session_state['game_mode'] == 'challenge':
        show_challenge_game()
    elif st.session_state['game_mode'] == 'footprint':
        show_footprint_game()
