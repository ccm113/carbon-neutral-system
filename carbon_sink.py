import streamlit as st
import plotly.graph_objects as go
from database import db

class CarbonSinkManager:
    """碳增汇管理组件"""
    
    SINK_TYPES = [
        "植树造林",
        "光伏发电",
        "风能发电",
        "节能改造",
        "公共交通",
        "垃圾分类",
        "绿色建筑",
        "其他"
    ]
    
    STATUS_MAP = {
        "pending": {"label": "待审核", "color": "#F39C12", "icon": "⏳"},
        "verified": {"label": "已认证", "color": "#27AE60", "icon": "✓"},
        "rejected": {"label": "已拒绝", "color": "#E74C3C", "icon": "✗"}
    }
    
    def __init__(self, user_id, data_processor):
        self.user_id = user_id
        self.data_processor = data_processor
    
    def get_carbon_balance(self):
        """计算碳平衡"""
        # 获取碳排放量
        emissions = self.data_processor.get_total_carbon_emission()
        
        # 获取已认证的碳汇量
        sinks = db.get_total_carbon_sink_amount(self.user_id)
        
        # 计算碳平衡
        balance = sinks - emissions
        
        # 计算碳中和进度
        if emissions > 0:
            progress = min(sinks / emissions * 100, 100)
        else:
            progress = 100 if sinks > 0 else 0
        
        return {
            "emissions": emissions,
            "sinks": sinks,
            "balance": balance,
            "progress": progress
        }
    
    def get_user_sinks(self):
        """获取用户碳汇记录"""
        return db.get_user_carbon_sinks(self.user_id)
    
    def add_sink(self, sink_type, amount, description):
        """添加碳汇记录"""
        return db.add_carbon_sink(self.user_id, sink_type, amount, description)
    
    def delete_sink(self, sink_id):
        """删除碳汇记录"""
        db.delete_carbon_sink(sink_id)
    
    def create_progress_gauge(self, progress):
        """创建碳中和进度仪表盘"""
        if progress >= 100:
            title_text = "🎉 已实现碳中和！"
            bar_color = "#27AE60"
        elif progress >= 80:
            title_text = f"碳中和进度 - {progress:.1f}%"
            bar_color = "#3498DB"
        elif progress >= 50:
            title_text = f"碳中和进度 - {progress:.1f}%"
            bar_color = "#F39C12"
        else:
            title_text = f"碳中和进度 - {progress:.1f}%"
            bar_color = "#E74C3C"
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title_text, 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#333"},
                'bar': {'color': bar_color},
                'steps': [
                    {'range': [0, 50], 'color': '#FFE5E5'},
                    {'range': [50, 80], 'color': '#FFF5E0'},
                    {'range': [80, 100], 'color': '#E8F5E9'}
                ],
                'threshold': {
                    'line': {'color': bar_color, 'width': 4},
                    'thickness': 0.75,
                    'value': progress
                }
            }
        ))
        
        fig.update_layout(height=250)
        return fig

def show_carbon_sink_page(data_processor):
    """显示碳增汇管理页面"""
    if 'user_id' not in st.session_state:
        st.warning("请先登录")
        return
    
    manager = CarbonSinkManager(st.session_state.user_id, data_processor)
    
    # 页面标题
    st.header("🌱 碳增汇管理")
    st.markdown("---")
    
    # 功能介绍
    with st.expander("📖 什么是碳增汇？", expanded=True):
        st.markdown("""
        **碳增汇**（Carbon Sink）是指通过各种方式吸收或减少大气中的二氧化碳，从而抵消自身产生的碳排放。
        
        **为什么需要碳增汇？**
        - 🌍 人类活动产生的碳排放导致全球气候变暖
        - ⚖️ 通过碳汇可以实现"碳中和"——即碳排放量与碳吸收量相等
        - 🌱 每个人都可以通过日常行动为减碳做出贡献
        
        **本功能可以帮您：**
        1. **记录碳汇行为**：如植树、使用清洁能源、垃圾分类等
        2. **计算碳平衡**：实时了解您的碳排放与碳汇的差值
        3. **追踪碳中和进度**：查看距离实现碳中和的目标还有多远
        
        **如何使用：**
        1. 在下方"添加碳汇记录"区域填写您的碳汇行为
        2. 选择碳汇类型，输入碳汇量（单位：kg CO₂）
        3. 提交后等待审核，审核通过后即可计入您的碳汇总量
        """)
    
    # 计算并显示碳平衡
    balance_data = manager.get_carbon_balance()
    
    # 碳平衡概览卡片
    st.subheader("碳平衡概览")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="累计碳排放量",
            value=f"{balance_data['emissions']:.1f} kg CO₂",
            delta="基于用电+出行数据",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            label="已认证碳汇量",
            value=f"{balance_data['sinks']:.1f} kg CO₂",
            delta="可用于抵消排放",
            delta_color="off"
        )
    
    with col3:
        balance_value = balance_data['balance']
        balance_label = "碳平衡"
        if balance_value >= 0:
            delta_text = "碳盈余"
            delta_color = "normal"
        else:
            delta_text = "碳赤字"
            delta_color = "inverse"
        
        st.metric(
            label=balance_label,
            value=f"{balance_value:.1f} kg CO₂",
            delta=delta_text,
            delta_color=delta_color
        )
    
    st.divider()
    
    # 碳中和进度
    st.subheader("碳中和进度")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        progress_fig = manager.create_progress_gauge(balance_data['progress'])
        st.plotly_chart(progress_fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        **碳中和目标说明：**
        
        - 当碳汇量 ≥ 碳排放量时，实现碳中和
        - 当前距离碳中和还差：**{:.1f} kg CO₂**
        
        **建议措施：**
        - 🌳 植树造林（每棵树约吸收15kg/年）
        - ☀️ 安装太阳能设备
        - 🚌 优先选择公共交通
        - 💡 实施节能改造
        """.format(max(0, balance_data['emissions'] - balance_data['sinks'])))
    
    st.divider()
    
    # 碳汇记录列表
    st.subheader("📋 我的碳汇记录")
    st.markdown("""
    这里显示您所有的碳汇记录。每条记录需要经过审核才能计入碳汇总量。
    
    **状态说明：**
    - ⏳ **待审核**：提交的记录正在等待审核，暂不计入碳汇总量
    - ✓ **已认证**：记录已通过审核，碳汇量已计入您的账户
    - ✗ **已拒绝**：记录未通过审核，可能是因为信息不完整或不符合要求
    
    **管理操作：**
    - 您可以删除不需要的记录
    - 审核中的记录也可以删除
    - 已认证的记录删除后会从碳汇总量中扣除
    """)
    
    sinks = manager.get_user_sinks()
    
    if sinks:
        # 统计信息
        total_sinks = sum(s[2] for s in sinks)
        verified_sinks = sum(s[2] for s in sinks if s[5] == 'verified')
        pending_count = sum(1 for s in sinks if s[5] == 'pending')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总碳汇记录", len(sinks))
        with col2:
            st.metric("已认证碳汇", f"{verified_sinks:.1f} kg")
        with col3:
            st.metric("待审核", pending_count)
        
        # 记录表格
        sink_data = []
        for sink in sinks:
            sink_id, sink_type, amount, date, desc, status = sink
            status_info = CarbonSinkManager.STATUS_MAP.get(status, {"label": status, "color": "#666", "icon": "?"})
            sink_data.append({
                "ID": sink_id,
                "类型": sink_type,
                "碳汇量(kg)": f"{amount:.1f}",
                "日期": date,
                "状态": f"<span style='color: {status_info['color']}; font-weight: bold;'>{status_info['icon']} {status_info['label']}</span>",
                "描述": desc if desc else "-"
            })
        
        # 转换为DataFrame显示
        import pandas as pd
        df = pd.DataFrame(sink_data)
        
        # 使用HTML渲染表格以支持颜色
        st.markdown("""
        <style>
        .dataframe table {width: 100%; border-collapse: collapse;}
        .dataframe th, .dataframe td {padding: 8px; text-align: left; border-bottom: 1px solid #ddd;}
        .dataframe th {background-color: #f8f9fa;}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # 删除按钮
        st.subheader("管理碳汇记录")
        sink_ids = [s[0] for s in sinks]
        selected_id = st.selectbox("选择要删除的记录ID", sink_ids)
        
        if st.button("删除选中记录", type="secondary"):
            manager.delete_sink(selected_id)
            st.success("记录已删除")
            st.rerun()
    
    else:
        st.info("暂无碳汇记录，点击下方添加您的第一条碳汇记录")
    
    st.divider()
    
    # 添加碳汇记录表单
    st.subheader("➕ 添加碳汇记录")
    st.markdown("""
    记录您的低碳行为，为地球减负！
    
    **填写指南：**
    1. **选择碳汇类型**：根据您的行为选择最符合的类型
    2. **输入相关数据**：根据类型输入数量、度数、里程等
    3. **系统自动计算**：碳汇量由系统根据您输入的数据自动计算
    4. **添加描述**：可选，但建议填写具体细节以便审核
    
    **提交后：**
    - 记录会进入"待审核"状态
    - 审核通过后，碳汇量会自动计入您的账户
    - 如果审核未通过，您可以修改后重新提交
    """)
    
    with st.form("add_sink_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sink_type = st.selectbox("碳汇类型", CarbonSinkManager.SINK_TYPES)
            
            # 根据碳汇类型显示不同的输入项
            if sink_type == "植树造林":
                input_value = st.number_input("种植树木数量（棵）", min_value=1, step=1)
                unit = "棵"
                conversion_factor = 15  # 每棵树约15kg CO₂/年
            elif sink_type == "光伏发电":
                input_value = st.number_input("光伏发电量（kWh）", min_value=1, step=1)
                unit = "kWh"
                conversion_factor = 0.58  # 1kWh约0.58kg CO₂
            elif sink_type == "风能发电":
                input_value = st.number_input("风能发电量（kWh）", min_value=1, step=1)
                unit = "kWh"
                conversion_factor = 0.01  # 1kWh约0.01kg CO₂
            elif sink_type == "节能改造":
                energy_saving = st.selectbox("节能改造类型", ["更换LED灯", "安装智能温控", "墙体保温", "其他"])
                input_value = st.number_input("预计年节电量（kWh）", min_value=1, step=1)
                unit = "kWh"
                conversion_factor = 0.58  # 节约1kWh约减少0.58kg CO₂
            elif sink_type == "公共交通":
                input_value = st.number_input("乘坐公共交通次数（次）", min_value=1, step=1)
                unit = "次"
                conversion_factor = 2  # 每次约减少2kg CO₂（相比自驾）
            elif sink_type == "垃圾分类":
                input_value = st.number_input("分类垃圾重量（kg）", min_value=1, step=1)
                unit = "kg"
                conversion_factor = 0.1  # 每kg分类垃圾约减少0.1kg CO₂
            elif sink_type == "绿色建筑":
                input_value = st.number_input("绿色建筑面积（㎡）", min_value=1, step=1)
                unit = "㎡"
                conversion_factor = 10  # 每㎡绿色建筑约减少10kg CO₂/年
            else:  # 其他
                input_value = st.number_input("碳汇量（kg CO₂）", min_value=0.1, step=0.1)
                unit = "kg CO₂"
                conversion_factor = 1  # 直接输入碳汇量
        
        with col2:
            # 显示计算结果
            calculated_amount = input_value * conversion_factor
            st.markdown(f"### 📊 计算结果")
            st.markdown(f"**输入值**: {input_value} {unit}")
            st.markdown(f"**碳汇量**: **{calculated_amount:.1f} kg CO₂**")
            
            description = st.text_area("详细描述（可选）", placeholder="例如：在社区种植了5棵树")
        
        submit_button = st.form_submit_button("保存碳汇记录")
        
        if submit_button:
            amount = input_value * conversion_factor
            if manager.add_sink(sink_type, amount, description):
                st.success(f"已添加 {amount:.1f} kg 的{CarbonSinkManager.STATUS_MAP['pending']['icon']} 待审核碳汇")
                st.rerun()
            else:
                st.error("添加失败，请重试")
    
    st.divider()
    
    # 碳汇类型说明
    st.subheader("📋 碳汇类型说明")
    st.markdown("""
    | 类型 | 说明 | 典型碳汇量参考 |
    |------|------|----------------|
    | 植树造林 | 种植树木吸收CO₂ | 每棵树约15kg/年 |
    | 光伏发电 | 使用太阳能减少化石能源使用 | 1kWh约0.58kg |
    | 风能发电 | 使用风能减少化石能源使用 | 1kWh约0.01kg |
    | 节能改造 | 提高能源效率减少排放 | 根据改造方案而定 |
    | 公共交通 | 选择低碳出行方式 | 相比自驾约减少80% |
    | 垃圾分类 | 减少垃圾处理碳排放 | 约10-50kg/月 |
    | 绿色建筑 | 低碳建筑设计与材料 | 根据建筑面积而定 |
    | 其他 | 其他碳汇行为 | 请在描述中说明 |
    """)
