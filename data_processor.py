import pandas as pd
import numpy as np
from datetime import datetime
from config import CARBON_FACTORS

def load_file(file_obj):
    """根据文件扩展名加载数据，支持CSV和Excel，支持UploadedFile对象"""
    # 获取文件名（处理UploadedFile对象和普通文件路径）
    if hasattr(file_obj, 'name'):
        filename = file_obj.name
    else:
        filename = str(file_obj)
    
    if filename.lower().endswith('.csv'):
        # 尝试多种编码读取
        encodings = ['utf-8-sig', 'gbk', 'gb2312', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                # 重置文件指针到开头
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                return pd.read_csv(file_obj, encoding=encoding)
            except:
                continue
        raise ValueError(f"无法读取文件，尝试了以下编码: {encodings}")
    elif filename.lower().endswith('.xlsx') or filename.lower().endswith('.xls'):
        return pd.read_excel(file_obj)
    else:
        raise ValueError(f"不支持的文件格式: {filename}")

class DataProcessor:
    def __init__(self):
        self.garbage_df = None
        self.electricity_df = None
        self.transport_df = None
    
    def load_csv_data(self, garbage_path=None, electricity_path=None, transport_path=None):
        """加载CSV数据"""
        if garbage_path:
            self.garbage_df = self._load_and_clean_garbage(garbage_path)
        if electricity_path:
            self.electricity_df = self._load_and_clean_electricity(electricity_path)
        if transport_path:
            self.transport_df = self._load_and_clean_transport(transport_path)
    
    def _load_and_clean_garbage(self, file_path):
        """加载并清洗垃圾分类数据"""
        df = load_file(file_path)
        
        # 数据清洗
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        df = df.dropna(subset=['日期', '投放类型', '是否正确分类'])
        df['是否正确分类'] = df['是否正确分类'].replace({'是': True, '否': False, 1: True, 0: False})
        df['频次'] = df['频次'].fillna(1).astype(int)
        
        return df
    
    def _load_and_clean_electricity(self, file_path):
        """加载并清洗用电数据（支持中文和英文字段名）"""
        df = load_file(file_path)
        
        # 支持英文字段名（Kaggle数据集格式）
        if 'Date' in df.columns and 'Time' in df.columns:
            # 构建字段映射（支持完整和截断的字段名）
            column_mapping = {
                'Date': '日期',
                'Time': '时间'
            }
            
            # 尝试匹配用电量字段（支持多种可能的字段名）
            possible_power_cols = ['Global_active_power', 'Global_active', 'Global_ac', 'Global_act']
            for col in possible_power_cols:
                if col in df.columns:
                    column_mapping[col] = '用电量(kWh)'
                    break
            
            df = df.rename(columns=column_mapping)
            
            # 合并日期和时间
            df['日期'] = pd.to_datetime(df['日期'] + ' ' + df['时间'], errors='coerce')
            
            # 根据时间推断用电时段
            df['用电时段'] = df['日期'].dt.hour.apply(lambda h: 
                '白天' if 6 <= h < 18 else ('傍晚' if 18 <= h < 22 else '夜晚'))
            
            # 根据用电量和时段推断用电设备
            df['用电设备'] = df.apply(lambda row: self._infer_device(row['用电量(kWh)'], row['用电时段']), axis=1)
            
        elif '日期' in df.columns:
            # 中文格式数据清洗
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        
        # 数据清洗
        df = df.dropna(subset=['日期', '用电量(kWh)'])
        df['用电量(kWh)'] = df['用电量(kWh)'].apply(lambda x: max(0, x))
        
        return df
    
    def _infer_device(self, consumption, period):
        """根据用电量和时段推断用电设备"""
        if consumption > 3:
            return '空调'
        elif consumption > 1.5:
            if period == '夜晚':
                return '热水器'
            else:
                return '洗衣机'
        elif consumption > 0.5:
            return '冰箱'
        else:
            return '照明'
    
    def _load_and_clean_transport(self, file_path):
        """加载并清洗出行数据"""
        df = load_file(file_path)
        
        # 数据清洗
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        df = df.dropna(subset=['日期', '出行方式', '出行距离(km)'])
        df['出行距离(km)'] = df['出行距离(km)'].apply(lambda x: max(0.1, x))
        
        return df
    
    def get_garbage_stats(self):
        """获取垃圾分类统计信息"""
        if self.garbage_df is None:
            return {}
        
        total_count = len(self.garbage_df)
        correct_count = self.garbage_df['是否正确分类'].sum()
        accuracy_rate = correct_count / total_count if total_count > 0 else 0
        
        # 按分类类型统计
        type_stats = self.garbage_df.groupby('投放类型')['是否正确分类'].agg(['count', 'sum'])
        type_stats['正确率'] = type_stats['sum'] / type_stats['count']
        
        # 按日期统计趋势（按周）
        weekly_stats = self.garbage_df.copy()
        weekly_stats['周'] = weekly_stats['日期'].dt.strftime('%Y-%m-%d')
        weekly_trend = weekly_stats.groupby('周')['是否正确分类'].mean()
        
        return {
            'total_count': total_count,
            'correct_count': int(correct_count),
            'accuracy_rate': accuracy_rate,
            'type_stats': type_stats,
            'weekly_trend': weekly_trend
        }
    
    def get_electricity_stats(self):
        """获取用电统计信息"""
        if self.electricity_df is None:
            return {}
        
        total_consumption = self.electricity_df['用电量(kWh)'].sum()
        avg_daily = self.electricity_df['用电量(kWh)'].mean()
        max_consumption = self.electricity_df['用电量(kWh)'].max()
        min_consumption = self.electricity_df['用电量(kWh)'].min()
        
        # 按时段统计
        time_stats = self.electricity_df.groupby('用电时段')['用电量(kWh)'].sum()
        
        # 按设备统计
        device_stats = self.electricity_df.groupby('用电设备')['用电量(kWh)'].sum()
        
        # 月度趋势
        monthly_stats = self.electricity_df.copy()
        monthly_stats['月'] = monthly_stats['日期'].dt.strftime('%Y-%m')
        monthly_trend = monthly_stats.groupby('月')['用电量(kWh)'].sum()
        
        # 计算碳排放
        carbon_emission = total_consumption * CARBON_FACTORS['electricity']
        
        return {
            'total_consumption': total_consumption,
            'avg_daily': avg_daily,
            'max_consumption': max_consumption,
            'min_consumption': min_consumption,
            'time_stats': time_stats,
            'device_stats': device_stats,
            'monthly_trend': monthly_trend,
            'carbon_emission': carbon_emission
        }
    
    def get_transport_stats(self):
        """获取出行统计信息"""
        if self.transport_df is None:
            return {}
        
        total_distance = self.transport_df['出行距离(km)'].sum()
        total_trips = len(self.transport_df)
        
        # 按出行方式统计
        mode_stats = self.transport_df.groupby('出行方式').agg({
            '出行距离(km)': 'sum',
            '油耗/电量(L/kWh)': 'sum'
        })
        mode_stats['出行次数'] = self.transport_df.groupby('出行方式').size()
        
        # 计算出行碳排放
        transport_carbon = 0
        for _, row in self.transport_df.iterrows():
            if row['出行方式'] == '私家车':
                if row['能源类型'] == '汽油':
                    transport_carbon += row['油耗/电量(L/kWh)'] * CARBON_FACTORS['gasoline']
                else:
                    transport_carbon += row['油耗/电量(L/kWh)'] * CARBON_FACTORS['diesel']
        
        # 绿色出行比例
        green_modes = ['步行', '自行车', '公交车', '地铁']
        green_trips = self.transport_df[self.transport_df['出行方式'].isin(green_modes)].shape[0]
        green_ratio = green_trips / total_trips if total_trips > 0 else 0
        
        return {
            'total_distance': total_distance,
            'total_trips': total_trips,
            'mode_stats': mode_stats,
            'carbon_emission': transport_carbon,
            'green_ratio': green_ratio
        }
    
    def get_total_carbon_emission(self):
        """计算总碳排放量"""
        elec_carbon = self.get_electricity_stats().get('carbon_emission', 0)
        transport_carbon = self.get_transport_stats().get('carbon_emission', 0)
        return elec_carbon + transport_carbon
    
    def get_all_stats(self):
        """获取所有统计信息"""
        return {
            'garbage': self.get_garbage_stats(),
            'electricity': self.get_electricity_stats(),
            'transport': self.get_transport_stats(),
            'total_carbon': self.get_total_carbon_emission()
        }
