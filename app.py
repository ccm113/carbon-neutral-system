import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 导入自定义模块
from database import db
from data_processor import DataProcessor
from user_profile import UserProfile
from llm_integration import LLMIntegration
from carbon_games_new import show_games_page

# 页面配置
st.set_page_config(
    page_title="碳循环与碳中和管理系统",
    page_icon="🌍",
    layout="wide"
)

# 初始化会话状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'llm_suggestions' not in st.session_state:
    st.session_state.llm_suggestions = ""
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 创建数据处理器实例（存储在session_state中，避免页面刷新时数据丢失）
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

data_processor = st.session_state.data_processor
llm = LLMIntegration()

def login():
    """登录页面"""
    st.title("🌱 居民低碳行为数据分析与智能减碳推荐系统")
    st.subheader("用户登录")
    
    # 加载记住的用户名
    import pickle
    saved_username = ""
    try:
        with open('data/saved_user.pkl', 'rb') as f:
            saved_username = pickle.load(f)
    except:
        pass
    
    # 登录表单
    with st.form("login_form"):
        username = st.text_input("用户名", value=saved_username)
        password = st.text_input("密码", type="password")
        remember_me = st.checkbox("记住用户名")
        submit_button = st.form_submit_button("登录")
        
        if submit_button:
            if db.verify_password(username, password):
                # 保存用户名
                if remember_me:
                    with open('data/saved_user.pkl', 'wb') as f:
                        pickle.dump(username, f)
                
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.user_id = db.get_user_id(username)
                st.success(f"欢迎回来，{username}！")
                st.rerun()
            else:
                st.error("用户名或密码错误")
    
    st.info("测试账户：user1/password1, user2/password2, admin/admin123")
    
    # 注册新用户
    st.divider()
    st.subheader("注册新用户")
    with st.form("register_form"):
        new_username = st.text_input("新用户名")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认密码", type="password")
        new_email = st.text_input("邮箱（可选）")
        register_button = st.form_submit_button("注册")
        
        if register_button:
            if not new_username or not new_password:
                st.error("用户名和密码不能为空")
            elif new_password != confirm_password:
                st.error("两次输入的密码不一致")
            elif db.add_user(new_username, new_password, new_email):
                st.success(f"用户 {new_username} 注册成功！请登录")
            else:
                st.error("用户名已存在")

def load_data():
    """数据加载页面"""
    st.header("📊 数据加载")
    
    # 使用默认数据
    if st.button("使用默认测试数据"):
        try:
            data_processor.load_csv_data(
                garbage_path='data/garbage_data.csv',
                electricity_path='data/electricity_data.csv',
                transport_path='data/transport_data.csv'
            )
            st.session_state.data_loaded = True
            st.success("数据加载成功！")
            
            # 生成用户画像
            profile_generator = UserProfile(data_processor)
            st.session_state.user_profile = profile_generator.generate_profile()
            st.rerun()
        except Exception as e:
            st.error(f"数据加载失败：{str(e)}")
    
    # 重新生成测试数据
    if st.button("🔄 重新生成测试数据"):
        try:
            from data_generator import DataGenerator
            generator = DataGenerator()
            generator.generate_all_data()
            st.success("测试数据重新生成成功！点击上方按钮加载新数据")
        except Exception as e:
            st.error(f"数据生成失败：{str(e)}")
    
    st.divider()
    
    # 自定义数据上传
    st.subheader("上传自定义数据")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        garbage_file = st.file_uploader("垃圾分类数据 (CSV/Excel)", type=["csv", "xlsx", "xls"])
    with col2:
        electricity_file = st.file_uploader("用电数据 (CSV/Excel)", type=["csv", "xlsx", "xls"])
    with col3:
        transport_file = st.file_uploader("出行数据 (CSV/Excel)", type=["csv", "xlsx", "xls"])
    
    if st.button("加载上传的数据"):
        try:
            data_processor.load_csv_data(
                garbage_path=garbage_file,
                electricity_path=electricity_file,
                transport_path=transport_file
            )
            st.session_state.data_loaded = True
            st.success("数据加载成功！")
            
            # 生成用户画像
            profile_generator = UserProfile(data_processor)
            st.session_state.user_profile = profile_generator.generate_profile()
            st.rerun()
        except Exception as e:
            st.error(f"数据加载失败：{str(e)}")

def show_statistics():
    """统计分析页面"""
    st.header("📈 统计分析")
    
    if not st.session_state.data_loaded:
        st.warning("请先加载数据")
        return
    
    stats = data_processor.get_all_stats()
    
    # 碳排放概览
    st.subheader("碳排放概览")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("用电碳排放", f"{stats['electricity'].get('carbon_emission', 0):.1f} kg CO2")
    with col2:
        st.metric("出行碳排放", f"{stats['transport'].get('carbon_emission', 0):.1f} kg CO2")
    with col3:
        st.metric("总碳排放量", f"{stats['total_carbon']:.1f} kg CO2")
    
    st.divider()
    
    # 垃圾分类统计
    st.subheader("垃圾分类统计")
    garbage_stats = stats['garbage']
    if garbage_stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总投放次数", garbage_stats['total_count'])
            st.metric("正确分类次数", garbage_stats['correct_count'])
            st.metric("正确率", f"{garbage_stats['accuracy_rate'] * 100:.1f}%")
        
        with col2:
            if not garbage_stats['type_stats'].empty:
                garbage_type_df = garbage_stats['type_stats'].reset_index()
                garbage_type_df['占比'] = (garbage_type_df['count'] / garbage_stats['total_count']) * 100
                garbage_type_df['正确率'] = (garbage_type_df['sum'] / garbage_type_df['count']) * 100
                garbage_type_df['说明'] = [
                    '可回收物：纸类、塑料、玻璃等，回收后可再利用',
                    '厨余垃圾：剩菜剩饭、果皮等，可堆肥处理',
                    '有害垃圾：电池、灯管、药品等，需特殊处理',
                    '其他垃圾：烟蒂、陶瓷、塑料袋等，焚烧或填埋'
                ][:len(garbage_type_df)]
                
                fig = px.pie(
                    garbage_type_df,
                    values='count',
                    names='投放类型',
                    title='垃圾分类投放分布',
                    labels={'count': '投放次数', '投放类型': '类型'}
                )
                fig.update_traces(
                    hovertemplate='<b>%{label}</b><br>' +
                                '投放次数: %{value} 次<br>' +
                                '<extra></extra>',
                    textinfo='percent+label',
                    textposition='inside'
                )
                fig.update_layout(legend=dict(orientation='v', yanchor='top', y=1, xanchor='right', x=1.2))
                st.plotly_chart(fig, use_container_width=True)
        
        # 正确率趋势
        if not garbage_stats['weekly_trend'].empty:
            weekly_df = garbage_stats['weekly_trend'].reset_index()
            weekly_df['正确率'] = weekly_df['是否正确分类'] * 100
            
            fig = px.line(
                weekly_df,
                x='周',
                y='是否正确分类',
                title='垃圾分类正确率趋势',
                hover_data={'正确率': ':,.1f%'},
                labels={'是否正确分类': '正确率', '周': '时间'}
            )
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>' +
                            '正确率: %{customdata[0]:.1f}%<br>' +
                            '<extra></extra>',
                line=dict(width=3, color='#3498DB'),
                marker=dict(size=8, symbol='circle', color='#3498DB')
            )
            fig.update_layout(
                yaxis_range=[0, 1],
                yaxis_tickformat='.0%',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 用电统计
    st.subheader("用电统计")
    elec_stats = stats['electricity']
    if elec_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总用电量", f"{elec_stats['total_consumption']:.1f} kWh")
        with col2:
            st.metric("日均用电", f"{elec_stats['avg_daily']:.1f} kWh")
        with col3:
            st.metric("用电碳排放", f"{elec_stats['carbon_emission']:.1f} kg CO2")
        
        # 用电时段分布
        col1, col2 = st.columns(2)
        with col1:
            if not elec_stats['time_stats'].empty:
                fig = px.bar(
                    elec_stats['time_stats'].reset_index(),
                    x='用电时段',
                    y='用电量(kWh)',
                    title='用电时段分布',
                    hover_data={
                        '用电量(kWh)': ':,.2f',
                        '说明': ['全天用电总量', '夜晚用电（通常包含空调、热水器）', '白天用电（通常为照明、电器）']
                    },
                    labels={'用电量(kWh)': '用电量', '用电时段': '时段'}
                )
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>' +
                                '用电量: %{y:.2f} kWh<br>' +
                                '说明: %{customdata[0]}<br>' +
                                '<extra></extra>',
                    marker=dict(line=dict(width=2, color='white'))
                )
                fig.update_layout(hovermode='closest')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not elec_stats['device_stats'].empty:
                device_df = elec_stats['device_stats'].reset_index()
                device_df['占比'] = (device_df['用电量(kWh)'] / elec_stats['total_consumption']) * 100
                device_df['说明'] = [
                    '热水器：通常是家庭用电主力，建议设置定时加热',
                    '空调：夏季/冬季用电高峰，建议温度设置在26°C左右',
                    '洗衣机：耗电与洗涤模式相关，建议集中洗涤',
                    '冰箱：24小时运行，建议定期除霜',
                    '电视：待机耗电不可忽视，建议及时关闭',
                    '电脑：工作用电，建议使用节能模式',
                    '照明：LED灯更节能，建议人走灯灭'
                ][:len(device_df)]
                
                fig = px.pie(
                    device_df,
                    values='用电量(kWh)',
                    names='用电设备',
                    title='用电设备分布',
                    labels={'用电量(kWh)': '用电量', '用电设备': '设备'}
                )
                fig.update_traces(
                    hovertemplate='<b>%{label}</b><br>' +
                                '用电量: %{value:.2f} kWh<br>' +
                                '<extra></extra>',
                    textinfo='percent+label',
                    textposition='inside'
                )
                fig.update_layout(legend=dict(orientation='v', yanchor='top', y=1, xanchor='right', x=1.2))
                st.plotly_chart(fig, use_container_width=True)
        
        # 月度趋势
        if not elec_stats['monthly_trend'].empty:
            monthly_df = elec_stats['monthly_trend'].reset_index()
            monthly_df['日均用电'] = monthly_df['用电量(kWh)'] / 30
            monthly_df['碳排放'] = monthly_df['用电量(kWh)'] * 0.581
            
            fig = px.line(
                monthly_df,
                x='月',
                y='用电量(kWh)',
                title='月度用电量趋势',
                hover_data={
                    '用电量(kWh)': ':,.2f',
                    '日均用电': ':,.2f',
                    '碳排放': ':,.2f'
                },
                labels={'用电量(kWh)': '用电量', '月': '月份'}
            )
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>' +
                            '月度用电量: %{y:.2f} kWh<br>' +
                            '日均用电: %{customdata[0]:.2f} kWh<br>' +
                            '碳排放量: %{customdata[1]:.2f} kg CO2<br>' +
                            '<extra></extra>',
                line=dict(width=3),
                marker=dict(size=8, symbol='circle')
            )
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 出行统计
    st.subheader("出行统计")
    transport_stats = stats['transport']
    if transport_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总出行次数", transport_stats['total_trips'])
        with col2:
            st.metric("总出行距离", f"{transport_stats['total_distance']:.1f} km")
        with col3:
            st.metric("绿色出行比例", f"{transport_stats['green_ratio'] * 100:.1f}%")
        
        # 出行方式分布
        if not transport_stats['mode_stats'].empty:
            transport_df = transport_stats['mode_stats'].reset_index()
            transport_df['占比'] = (transport_df['出行次数'] / transport_stats['total_trips']) * 100
            transport_df['类型'] = ['绿色出行' if m in ['步行', '自行车', '公交车', '地铁'] else '非绿色出行' 
                                  for m in transport_df['出行方式']]
            transport_df['说明'] = [
                '步行：零碳排放，最环保的出行方式',
                '自行车：零碳排放，有益健康',
                '公交车：低碳出行，建议优先选择',
                '地铁：低碳出行，快速便捷',
                '私家车：碳排放较高，建议减少使用'
            ][:len(transport_df)]
            
            fig = px.bar(
                transport_df,
                x='出行方式',
                y='出行次数',
                title='出行方式分布',
                color='类型',
                color_discrete_map={'绿色出行': '#2ECC71', '非绿色出行': '#E74C3C'},
                hover_data={
                    '出行次数': ':,.0f',
                    '占比': ':,.1f%',
                    '类型': True,
                    '说明': True
                },
                labels={'出行次数': '次数', '出行方式': '方式'}
            )
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>' +
                            '出行次数: %{y} 次<br>' +
                            '占比: %{customdata[0]:.1f}%<br>' +
                            '类型: %{customdata[1]}<br>' +
                            '说明: %{customdata[2]}<br>' +
                            '<extra></extra>',
                marker=dict(line=dict(width=2, color='white'))
            )
            fig.update_layout(hovermode='closest')
            st.plotly_chart(fig, use_container_width=True)

def show_user_profile():
    """用户画像页面"""
    st.header("👤 用户低碳画像")
    
    if not st.session_state.user_profile:
        st.warning("请先加载数据")
        return
    
    profile = st.session_state.user_profile
    
    # 综合评分
    st.subheader("综合评估")
    score = profile['total_score']
    level = profile['level']
    
    # 综合评分仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"综合评分 - {level['level']}", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#333"},
            'bar': {'color': '#DC143C'},  # 深红指针（更高饱和度）
            'steps': [
                {'range': [0, 50], 'color': '#FF6B6B'},  # 高饱和红色
                {'range': [50, 70], 'color': '#FFD93D'},  # 高饱和黄色
                {'range': [70, 85], 'color': '#9B59B6'},  # 高饱和紫色
                {'range': [85, 100], 'color': '#2ECC71'}  # 高饱和绿色
            ],
            'threshold': {
                'line': {'color': "#DC143C", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=350)
    
    # 综合评分仪表盘和颜色说明并排显示
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
        st.info(level['description'])
    
    with col2:
        # 仪表盘颜色说明
        st.markdown("""
        **仪表盘颜色说明：**
        | 颜色 | 分数范围 | 含义 |
        |------|----------|------|
        | 🔴 红色 | 0-50分 | 低碳新手 |
        | 🟡 黄色 | 50-70分 | 低碳学习者 |
        | 🟣 紫色 | 70-85分 | 低碳践行者 |
        | 🟢 绿色 | 85-100分 | 低碳达人 |
        """)
    
    # 各项得分展示（并排仪表盘）
    st.subheader("各项得分")
    
    # 获取有数据的项（使用高饱和度颜色）
    available_items = []
    if profile.get('has_electricity') and profile['electricity_score'] is not None:
        available_items.append(('用电习惯', profile['electricity_score'], '#3498DB'))  # 蓝色
    if profile.get('has_transport') and profile['transport_score'] is not None:
        available_items.append(('出行方式', profile['transport_score'], '#E74C3C'))  # 红色（高饱和）
    if profile.get('has_garbage') and profile['garbage_score'] is not None:
        available_items.append(('垃圾分类', profile['garbage_score'], '#F39C12'))  # 橙色
    
    # 创建并排仪表盘（增大尺寸），右侧显示图例
    if available_items:
        # 创建主区域和图例区域
        main_cols = st.columns([3, 1])
        
        with main_cols[0]:
            cols = st.columns(len(available_items))
            for i, (name, item_score, color) in enumerate(available_items):
                with cols[i]:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=item_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': name, 'font': {'size': 16}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#333"},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, 50], 'color': '#FF6B6B'},  # 高饱和红色
                                {'range': [50, 70], 'color': '#FFD93D'},  # 高饱和黄色
                                {'range': [70, 85], 'color': '#9B59B6'},  # 高饱和紫色
                                {'range': [85, 100], 'color': '#2ECC71'}  # 高饱和绿色
                            ]
                        }
                    ))
                    fig.update_layout(height=280)
                    st.plotly_chart(fig, use_container_width=True)
        
        with main_cols[1]:
            # 分项指针颜色图例
            st.markdown("""
            **分项指针颜色：**
            | 颜色 | 维度 |
            |------|------|
            | 🔵 蓝色 | 用电习惯 |
            | 🔴 红色 | 出行方式 |
            | 🟠 橙色 | 垃圾分类 |
            """)
    
    # 低碳职级等级榜
    st.subheader("🏆 低碳职级等级榜")
    
    # 定义职级等级（由低到高）及说明
    levels = [
        {'name': '低碳见习', 'emoji': '👶', 'min_score': 0, 'max_score': 10, 'short': 'CT', 'desc': '初入低碳领域，开始学习低碳生活知识'},
        {'name': '低碳助理', 'emoji': '🧑‍💼', 'min_score': 10, 'max_score': 20, 'short': 'CA', 'desc': '了解基本低碳知识，开始实践低碳行为'},
        {'name': '低碳专员', 'emoji': '👨‍💼', 'min_score': 20, 'max_score': 30, 'short': 'CSY', 'desc': '掌握基础低碳技能，养成初步低碳习惯'},
        {'name': '低碳主管', 'emoji': '👩‍💼', 'min_score': 30, 'max_score': 40, 'short': 'CS', 'desc': '能够管理个人碳排放，影响身边人'},
        {'name': '低碳经理', 'emoji': '💼', 'min_score': 40, 'max_score': 50, 'short': 'CM', 'desc': '精通低碳生活方式，有显著减碳成效'},
        {'name': '低碳总监', 'emoji': '🎯', 'min_score': 50, 'max_score': 60, 'short': 'CDO', 'desc': '成为低碳生活专家，指导他人实践'},
        {'name': '低碳顾问', 'emoji': '🤝', 'min_score': 60, 'max_score': 70, 'short': 'CCA', 'desc': '能够提供专业低碳咨询，影响社区'},
        {'name': '低碳首席', 'emoji': '👑', 'min_score': 70, 'max_score': 80, 'short': 'CEO', 'desc': '低碳领域权威，引领低碳风尚'},
        {'name': '低碳执行官', 'emoji': '🌟', 'min_score': 80, 'max_score': 90, 'short': 'CXO', 'desc': '卓越低碳践行者，成为榜样人物'},
        {'name': '低碳领航官', 'emoji': '🚀', 'min_score': 90, 'max_score': 101, 'short': 'LGO', 'desc': '低碳领域领袖，推动社会低碳转型'}
    ]
    
    # 确定用户当前等级（使用精确匹配）
    current_level = None
    current_level_name = ""
    for level in levels:
        if level['min_score'] <= score < level['max_score']:
            current_level = level
            current_level_name = level['name']
            break
    
    # 显示当前分数（调试用）
    st.markdown(f"**当前综合评分：{score:.1f}分**")
    
    # 使用居中布局构建金字塔（只渲染一次）
    rendered_levels = []
    for i, level in enumerate(reversed(levels)):
        if level['name'] in rendered_levels:
            continue
        rendered_levels.append(level['name'])
        
        is_active = level['name'] == current_level_name
        is_passed = score >= level['max_score']
        
        # 计算金字塔每层的宽度百分比（越高层越窄）
        width_pct = max(15, 85 - i * 7)
        
        if is_active:
            st.markdown(f"""
            <div style="
                width: {width_pct}%;
                margin: 4px auto;
                background: linear-gradient(135deg, #FFD700, #FFA500);
                color: white;
                padding: 6px 16px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                box-shadow: 0 2px 12px rgba(255, 215, 0, 0.5);
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                cursor: pointer;
            " title="分数范围: {level['min_score']}-{level['max_score']-1}分\n说明: {level['desc']}">
                <span style="font-size: 18px;">{level['emoji']}</span>
                <span style="font-size: 14px;">{level['name']}</span>
                <span style="font-size: 12px; opacity: 0.85;">【{level['short']}】</span>
                <span style="font-size: 11px; opacity: 0.9;">({level['min_score']}-{level['max_score']-1}分)</span>
            </div>
            """, unsafe_allow_html=True)
        elif is_passed:
            st.markdown(f"""
            <div style="
                width: {width_pct}%;
                margin: 4px auto;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 6px 16px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                cursor: pointer;
            " title="分数范围: {level['min_score']}-{level['max_score']-1}分\n说明: {level['desc']}">
                <span style="font-size: 18px;">{level['emoji']}</span>
                <span style="font-size: 14px;">{level['name']}</span>
                <span style="font-size: 12px; opacity: 0.85;">【{level['short']}】</span>
                <span style="font-size: 11px; opacity: 0.9;">({level['min_score']}-{level['max_score']-1}分)</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                width: {width_pct}%;
                margin: 4px auto;
                background: linear-gradient(135deg, #f5f5f5, #e8e8e8);
                color: #666;
                padding: 6px 16px;
                border-radius: 8px;
                text-align: center;
                opacity: 0.5;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                cursor: pointer;
            " title="分数范围: {level['min_score']}-{level['max_score']-1}分\n说明: {level['desc']}">
                <span style="font-size: 18px;">{level['emoji']}</span>
                <span style="font-size: 14px;">{level['name']}</span>
                <span style="font-size: 12px;">【{level['short']}】</span>
                <span style="font-size: 11px;">({level['min_score']}-{level['max_score']-1}分)</span>
            </div>
            """, unsafe_allow_html=True)
    
    # 当前等级说明
    if current_level:
        st.success(f"🎉 恭喜！您当前的职级是「{current_level['emoji']} {current_level['name']}【{current_level['short']}】」")
        # 计算下一级所需分数
        next_idx = levels.index(current_level) + 1
        if next_idx < len(levels):
            next_level = levels[next_idx]
            needed_score = next_level['min_score'] - score
            st.info(f"距离下一级「{next_level['emoji']} {next_level['name']}【{next_level['short']}】」还需要 {needed_score:.1f} 分")
    
    # 碳排放解读
    st.subheader("🌍 碳排放解读")
    total_carbon = profile['stats']['total_carbon']
    
    # 碳排放等级评估
    if total_carbon < 200:
        carbon_level = "低碳"
        carbon_color = "#2ECC71"
        carbon_desc = "表现优秀！您的碳排放量低于平均水平"
    elif total_carbon < 500:
        carbon_level = "中等"
        carbon_color = "#FFD93D"
        carbon_desc = "表现一般，还有改进空间"
    elif total_carbon < 1000:
        carbon_level = "偏高"
        carbon_color = "#F39C12"
        carbon_desc = "需要关注，建议采取减碳措施"
    else:
        carbon_level = "高碳"
        carbon_color = "#E74C3C"
        carbon_desc = "碳排放量较高，建议立即采取行动"
    
    # 直观对比数据
    trees_absorbed = total_carbon / 15  # 一棵树年吸收约15kg CO2
    km_driven = total_carbon / 0.18     # 汽车每公里约排放0.18kg CO2
    light_bulb_hours = total_carbon * 17.2  # 1kWh=0.581kg CO2，100W灯泡1小时=0.1kWh
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="当前碳排放量", value=f"{total_carbon:.1f} kg CO2", delta=carbon_level, delta_color="off")
    with col2:
        st.metric(label="相当于砍伐树木", value=f"{trees_absorbed:.1f} 棵", help="一棵树每年约吸收15kg CO2")
    with col3:
        st.metric(label="相当于汽车行驶", value=f"{km_driven:.1f} 公里", help="普通汽车每公里约排放0.18kg CO2")
    
    st.markdown(f"""
    <div style="background: {carbon_color}20; padding: 12px; border-radius: 8px; border-left: 4px solid {carbon_color};">
        <strong style="color: {carbon_color};">{carbon_desc}</strong>
        <p style="color: #666; margin-top: 8px;">
        💡 小贴士：减少 {total_carbon * 0.3:.1f} kg CO2 相当于种植 {trees_absorbed * 0.3:.1f} 棵树，或者减少 {km_driven * 0.3:.1f} 公里的自驾出行。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 碳排放参考标准
    st.markdown("""
    **碳排放参考标准（年度）：**
    
    | 水平 | 碳排放量 | 说明 |
    |------|----------|------|
    | 🌱 优秀 | < 200 kg | 低碳生活典范 |
    | 🟢 良好 | 200-500 kg | 高于平均水平 |
    | 🟡 一般 | 500-1000 kg | 需要改进 |
    | 🔴 较高 | > 1000 kg | 需要采取行动 |
    
    **参考数据：**
    - 中国人均年碳排放量：约4.5吨（4500kg）
    - 全球人均年碳排放量：约4.9吨（4900kg）
    - 本系统统计范围：用电 + 出行碳排放
    """)
    
    # 短板分析
    st.subheader("⚠️ 碳排放短板")
    if profile['weaknesses']:
        for weakness in profile['weaknesses']:
            with st.container():
                st.markdown(f"**{weakness['category']}**")
                st.markdown(f"等级：{weakness['level']}（得分：{weakness['score']}分）")
                st.markdown(f"建议：{weakness['suggestion']}")
                st.divider()
    else:
        st.success("🎉 暂无明显短板，继续保持！")

def show_analysis_report():
    """分析报告页面"""
    st.header("📄 个人低碳生活分析报告")
    
    if not st.session_state.user_profile:
        st.warning("请先加载数据")
        return
    
    if not st.session_state.analysis_report:
        with st.spinner("正在生成分析报告..."):
            st.session_state.analysis_report = llm.generate_analysis_report(st.session_state.user_profile)
    
    st.write(st.session_state.analysis_report)
    
    if st.button("重新生成报告"):
        with st.spinner("正在重新生成..."):
            st.session_state.analysis_report = llm.generate_analysis_report(st.session_state.user_profile)
        st.rerun()

def show_ai_chat():
    """AI智能问答页面"""
    st.header("🤖 AI智能问答")
    
    # 检查是否有用户画像数据
    has_profile = st.session_state.get('user_profile') is not None
    
    # 提示用户已加载的数据
    if has_profile:
        profile = st.session_state.user_profile
        st.info(f"""
        📊 当前已加载分析数据：
        - 综合评分：{profile['total_score']:.1f}分
        - 低碳职级：{profile['level']['level']}
        - 总碳排放量：{profile['stats']['total_carbon']:.1f} kg CO2
        """)
    else:
        st.warning("⚠️ 您尚未加载数据进行分析。AI将基于通用知识回答问题。")
    
    # 清除历史记录按钮
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 清除历史", key="clear_chat_history"):
            st.session_state.chat_history = []
            llm.clear_history()
            st.rerun()
    
    # 计算耗能功能入口
    with st.expander("⚡ 计算耗能", expanded=False):
        st.subheader("家电耗电量计算器")
        
        # 家电类型选择
        appliance_options = ['空调', '热水器', '洗衣机', '冰箱', '电视', '电脑', '照明', '电饭煲', '微波炉', '电磁炉', '其他']
        selected_appliance = st.selectbox("选择家电类型", appliance_options)
        
        # 功率输入
        power = st.number_input("功率 (W)", min_value=1, max_value=5000, value=1000)
        
        # 挡位选择
        gear_options = ['默认', '低挡', '中挡', '高挡', '节能', '静音']
        selected_gear = st.selectbox("挡位模式", gear_options)
        
        # 使用时间输入
        hours = st.number_input("使用时间 (小时)", min_value=0.1, max_value=24.0, value=1.0, step=0.5)
        
        # 电价（可选）
        electricity_price = st.number_input("电价 (元/kWh)", min_value=0.1, max_value=2.0, value=0.6, step=0.01)
        
        # 计算按钮
        if st.button("计算", use_container_width=True):
            # 挡位系数
            gear_coeff = {'默认': 1.0, '低挡': 0.7, '中挡': 1.0, '高挡': 1.5, '节能': 0.5, '静音': 0.6}
            coeff = gear_coeff[selected_gear]
            
            # 计算实际功率
            actual_power = int(power * coeff)
            
            # 计算用电量：用电量(kWh) = 功率(W) × 时间(h) ÷ 1000
            kwh = (actual_power * hours) / 1000
            
            # 计算碳排放量：碳排放(kg CO2) = 用电量(kWh) × 0.581
            carbon = kwh * 0.581
            
            # 计算费用
            cost = kwh * electricity_price
            
            # 显示结果
            st.success(f"""
            **{selected_appliance}用电计算结果：**
            - 功率：{actual_power}W（{selected_gear}模式）
            - 使用时间：{hours:.1f}小时
            - 用电量：{kwh:.2f} kWh（度）
            - 碳排放量：{carbon:.2f} kg CO2
            - 预计电费：{cost:.2f} 元
            
            📝 计算公式：用电量 = 功率(W) × 时间(h) ÷ 1000
            """)
    
    # 显示聊天历史
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])
    
    # 输入框
    user_input = st.chat_input("请输入您的问题...")
    if user_input:
        # 添加用户消息
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # 显示用户消息
        with st.chat_message('user'):
            st.write(user_input)
        
        # 获取用户画像数据
        user_profile = st.session_state.get('user_profile')
        
        # 生成AI回复
        with st.chat_message('assistant'):
            with st.spinner("AI正在思考..."):
                response = llm.answer_question(user_input, user_profile)
                st.write(response)
        
        # 添加AI消息到历史
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})

def main():
    """主应用程序"""
    if not st.session_state.logged_in:
        login()
        return
    
    # 侧边栏导航
    with st.sidebar:
        st.title(f"欢迎, {st.session_state.current_user}")
        st.divider()
        
        menu = ["📊 数据加载", "📈 统计分析", "👤 用户画像", "🎮 碳游戏", "📄 分析报告", "🤖 AI问答"]
        menu_ids = ["数据加载", "统计分析", "用户画像", "碳游戏", "分析报告", "AI问答"]
        
        # 初始化当前选择
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "数据加载"
        
        # 创建导航按钮
        for label, menu_id in zip(menu, menu_ids):
            is_active = menu_id == st.session_state.current_page
            button_type = "primary" if is_active else "secondary"
            
            if st.button(label, key=f"nav-{menu_id}", use_container_width=True, type=button_type):
                st.session_state.current_page = menu_id
                st.rerun()
        
        st.divider()
        
        # 登出按钮
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.data_loaded = False
            st.session_state.user_profile = None
            st.rerun()
    
    choice = st.session_state.current_page
    
    # 主内容区
    st.title("🌍 碳循环与碳中和管理系统")
    st.markdown("---")
    
    if choice == "数据加载":
        load_data()
    elif choice == "统计分析":
        show_statistics()
    elif choice == "用户画像":
        show_user_profile()
    elif choice == "碳游戏":
        show_games_page()
    elif choice == "分析报告":
        show_analysis_report()
    elif choice == "AI问答":
        show_ai_chat()

if __name__ == "__main__":
    main()
