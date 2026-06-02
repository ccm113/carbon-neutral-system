import plotly.graph_objects as go
import pandas as pd

class CarbonCycleVisualizer:
    """碳循环可视化组件"""
    
    def __init__(self):
        # 碳循环数据（单位：Gt CO₂/年）
        self.carbon_data = {
            "sources": ["大气CO₂", "化石燃料", "废弃物"],
            "sinks": ["植被吸收", "土壤固碳", "海洋吸收", "燃烧排放", "焚烧处理", "资源化利用"],
            "flows": [
                {"source": "大气CO₂", "target": "植被吸收", "value": 250, "label": "光合作用"},
                {"source": "大气CO₂", "target": "海洋吸收", "value": 220, "label": "海洋溶解"},
                {"source": "化石燃料", "target": "燃烧排放", "value": 350, "label": "能源消耗"},
                {"source": "废弃物", "target": "焚烧处理", "value": 80, "label": "垃圾焚烧"},
                {"source": "废弃物", "target": "资源化利用", "value": 40, "label": "回收利用"},
                {"source": "燃烧排放", "target": "大气CO₂", "value": 350, "label": "排入大气"},
                {"source": "焚烧处理", "target": "大气CO₂", "value": 60, "label": "排放"},
                {"source": "植被吸收", "target": "土壤固碳", "value": 100, "label": "落叶腐殖"},
                {"source": "植被吸收", "target": "大气CO₂", "value": 150, "label": "呼吸作用"},
                {"source": "土壤固碳", "target": "大气CO₂", "value": 50, "label": "微生物分解"},
                {"source": "海洋吸收", "target": "大气CO₂", "value": 200, "label": "海洋释放"},
            ]
        }
        
        # 节点颜色映射
        self.node_colors = {
            "大气CO₂": "#87CEEB",      # 天蓝色
            "化石燃料": "#8B4513",     # 棕色
            "废弃物": "#696969",       # 灰色
            "植被吸收": "#228B22",     # 森林绿
            "土壤固碳": "#CD853F",     # 秘鲁色
            "海洋吸收": "#1E90FF",     # 道奇蓝
            "燃烧排放": "#FF4500",     # 橙红
            "焚烧处理": "#FF6347",     # 番茄红
            "资源化利用": "#32CD32",   # 酸橙绿
        }
    
    def get_all_nodes(self):
        """获取所有节点"""
        return list(set(self.carbon_data["sources"] + self.carbon_data["sinks"]))
    
    def create_sankey_diagram(self):
        """创建碳循环桑基图"""
        nodes = self.get_all_nodes()
        node_indices = {node: i for i, node in enumerate(nodes)}
        
        source_indices = []
        target_indices = []
        values = []
        labels = []
        
        for flow in self.carbon_data["flows"]:
            source_indices.append(node_indices[flow["source"]])
            target_indices.append(node_indices[flow["target"]])
            values.append(flow["value"])
            labels.append(flow["label"])
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="black", width=1),
                label=nodes,
                color=[self.node_colors[node] for node in nodes],
                hovertemplate='<b>%{label}</b><br>点击查看详情<extra></extra>'
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                label=labels,
                hovertemplate='<b>%{label}</b><br>碳流量: %{value} Gt CO₂/年<extra></extra>',
                color="rgba(100, 100, 100, 0.3)"
            )
        )])
        
        fig.update_layout(
            title_text="🌍 全球碳循环流向图",
            title_font=dict(size=20, color="#2c3e50"),
            font=dict(size=14, color="#34495e"),
            width=900,
            height=600,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        return fig
    
    def create_carbon_stock_chart(self):
        """创建碳储量图表"""
        stock_data = pd.DataFrame({
            "碳库": ["大气", "海洋表层", "陆地植被", "土壤", "化石燃料"],
            "碳储量(Gt)": [780, 1050, 550, 2300, 4130],
            "类型": ["活跃碳库", "活跃碳库", "活跃碳库", "缓慢碳库", "地质碳库"]
        })
        
        fig = px.bar(
            stock_data,
            x="碳库",
            y="碳储量(Gt)",
            color="类型",
            color_discrete_map={
                "活跃碳库": "#3498DB",
                "缓慢碳库": "#F39C12",
                "地质碳库": "#9B59B6"
            },
            title="📦 全球主要碳库储量",
            labels={"碳储量(Gt)": "碳储量 (Gt CO₂)"},
            hover_data={"碳储量(Gt)": ":,.0f"}
        )
        
        fig.update_layout(
            font=dict(size=14),
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        return fig
    
    def get_carbon_facts(self):
        """获取碳循环科普知识"""
        return [
            {
                "title": "🌿 碳循环基本概念",
                "content": "碳循环是碳元素在地球各圈层（大气、海洋、陆地、生物圈）之间的循环流动过程。人类活动正在打破自然平衡。"
            },
            {
                "title": "🔥 人类活动的影响",
                "content": "工业革命以来，人类通过燃烧化石燃料已向大气释放超过5000亿吨CO₂，导致大气CO₂浓度从280ppm上升到420ppm。"
            },
            {
                "title": "🌊 海洋的作用",
                "content": "海洋吸收了约30%的人为碳排放，是重要的碳汇。但过量吸收导致海水酸化，影响海洋生态系统。"
            },
            {
                "title": "🌳 森林的角色",
                "content": "森林通过光合作用吸收CO₂并储存于植被和土壤中。全球森林每年吸收约250亿吨CO₂，相当于化石燃料排放量的三分之一。"
            }
        ]
    
    def get_human_impact_data(self):
        """获取人类活动影响数据"""
        return pd.DataFrame({
            "活动类型": ["化石燃料燃烧", "土地利用变化", "水泥生产", "废弃物处理"],
            "年排放量(Gt CO₂)": [35, 5, 2, 1],
            "占比(%)": [82, 12, 5, 1]
        })

import plotly.express as px

def show_carbon_cycle_page():
    """显示碳循环可视化页面"""
    visualizer = CarbonCycleVisualizer()
    
    # 页面标题
    st.header("🌍 碳循环可视化")
    st.markdown("---")
    
    # 桑基图
    st.subheader("碳循环流向图")
    sankey_fig = visualizer.create_sankey_diagram()
    st.plotly_chart(sankey_fig, use_container_width=True)
    
    # 图例说明
    st.markdown("""
    **图例说明：**
    | 节点 | 颜色 | 说明 |
    |------|------|------|
    | 大气CO₂ | 天蓝色 | 大气中的二氧化碳 |
    | 化石燃料 | 棕色 | 煤炭、石油、天然气 |
    | 废弃物 | 灰色 | 生活垃圾和工业废弃物 |
    | 植被吸收 | 森林绿 | 植物光合作用吸收CO₂ |
    | 土壤固碳 | 秘鲁色 | 土壤中的有机碳储存 |
    | 海洋吸收 | 道奇蓝 | 海洋溶解吸收CO₂ |
    | 燃烧排放 | 橙红色 | 化石燃料燃烧释放 |
    | 焚烧处理 | 番茄红 | 垃圾焚烧释放 |
    | 资源化利用 | 酸橙绿 | 废弃物回收再利用 |
    """)
    
    st.divider()
    
    # 两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        # 碳储量图表
        st.subheader("全球碳库储量")
        stock_fig = visualizer.create_carbon_stock_chart()
        st.plotly_chart(stock_fig, use_container_width=True)
    
    with col2:
        # 人类活动影响
        st.subheader("人类活动碳排放")
        impact_data = visualizer.get_human_impact_data()
        fig = px.pie(
            impact_data,
            values="年排放量(Gt CO₂)",
            names="活动类型",
            title="人为碳排放来源分布",
            hole=0.4,
            hover_data={"年排放量(Gt CO₂)": ":,.1f", "占比(%)": ":,.1f"}
        )
        fig.update_layout(font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 科普知识卡片
    st.subheader("📚 碳循环科普")
    facts = visualizer.get_carbon_facts()
    for fact in facts:
        with st.expander(fact["title"]):
            st.write(fact["content"])

# 确保streamlit已导入
try:
    import streamlit as st
except ImportError:
    pass
