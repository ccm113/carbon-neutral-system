import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataGenerator:
    """数据生成器 - 根据问卷数据生成模拟行为数据"""
    
    def __init__(self):
        self.garbage_types = ['厨余垃圾', '可回收物', '有害垃圾', '其他垃圾']
        self.electricity_devices = ['空调', '冰箱', '洗衣机', '照明', '电脑', '电视', '热水器']
        self.electricity_periods = ['白天', '夜晚', '全天']
        self.transport_modes = ['私家车', '公交车', '地铁', '步行', '自行车']
        self.transport_purposes = ['上班', '上学', '购物', '休闲', '其他']
        self.energy_types = ['汽油', '柴油', '电']
    
    def generate_garbage_data(self, num_records=300):
        """生成垃圾分类数据"""
        dates = []
        types = []
        corrects = []
        frequencies = []
        
        start_date = datetime(2024, 1, 1)
        for i in range(num_records):
            dates.append(start_date + timedelta(days=random.randint(0, 364)))
            types.append(random.choice(self.garbage_types))
            corrects.append(random.random() > 0.2)  # 80%正确率
            frequencies.append(1)
        
        df = pd.DataFrame({
            '日期': dates,
            '投放类型': types,
            '是否正确分类': corrects,
            '频次': frequencies
        })
        df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
        df['是否正确分类'] = df['是否正确分类'].astype(int)
        return df
    
    def generate_electricity_data(self, num_records=200):
        """生成用电数据"""
        dates = []
        consumptions = []
        periods = []
        devices = []
        
        start_date = datetime(2024, 1, 1)
        for i in range(num_records):
            dates.append(start_date + timedelta(days=random.randint(0, 364)))
            device = random.choice(self.electricity_devices)
            devices.append(device)
            
            # 根据设备类型生成用电量
            if device == '空调':
                consumption = random.uniform(1.5, 8.0)
            elif device == '热水器':
                consumption = random.uniform(2.0, 6.0)
            elif device == '洗衣机':
                consumption = random.uniform(0.5, 2.0)
            elif device == '冰箱':
                consumption = random.uniform(0.8, 1.5)
            else:
                consumption = random.uniform(0.1, 1.0)
            
            consumptions.append(round(consumption, 2))
            periods.append(random.choice(self.electricity_periods))
        
        df = pd.DataFrame({
            '日期': dates,
            '用电量(kWh)': consumptions,
            '用电时段': periods,
            '用电设备': devices
        })
        df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
        return df
    
    def generate_transport_data(self, num_records=400):
        """生成出行数据"""
        dates = []
        modes = []
        distances = []
        energy_types = []
        consumptions = []
        purposes = []
        
        start_date = datetime(2024, 1, 1)
        for i in range(num_records):
            dates.append(start_date + timedelta(days=random.randint(0, 364)))
            mode = random.choices(
                self.transport_modes,
                weights=[0.3, 0.25, 0.2, 0.15, 0.1]
            )[0]
            modes.append(mode)
            
            # 根据出行方式生成距离
            if mode in ['步行', '自行车']:
                distance = random.uniform(0.5, 3.0)
                energy_type = '-'
                consumption = 0
            elif mode == '公交车':
                distance = random.uniform(2.0, 15.0)
                energy_type = '电'
                consumption = random.uniform(0.5, 2.0)
            elif mode == '地铁':
                distance = random.uniform(3.0, 20.0)
                energy_type = '电'
                consumption = random.uniform(0.8, 3.0)
            else:  # 私家车
                distance = random.uniform(5.0, 50.0)
                energy_type = random.choice(['汽油', '柴油'])
                consumption = distance * random.uniform(0.05, 0.12)
            
            distances.append(round(distance, 2))
            energy_types.append(energy_type)
            consumptions.append(round(consumption, 2))
            purposes.append(random.choice(self.transport_purposes))
        
        df = pd.DataFrame({
            '日期': dates,
            '出行方式': modes,
            '出行距离(km)': distances,
            '能源类型': energy_types,
            '油耗/电量(L/kWh)': consumptions,
            '出行目的': purposes
        })
        df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
        return df
    
    def generate_all_data(self, garbage_count=300, electricity_count=200, transport_count=400):
        """生成所有类型的数据"""
        garbage_df = self.generate_garbage_data(garbage_count)
        electricity_df = self.generate_electricity_data(electricity_count)
        transport_df = self.generate_transport_data(transport_count)
        
        # 保存到文件
        garbage_df.to_csv('data/garbage_data.csv', index=False, encoding='utf-8-sig')
        electricity_df.to_csv('data/electricity_data.csv', index=False, encoding='utf-8-sig')
        transport_df.to_csv('data/transport_data.csv', index=False, encoding='utf-8-sig')
        
        return garbage_df, electricity_df, transport_df

# 生成测试数据
if __name__ == '__main__':
    generator = DataGenerator()
    generator.generate_all_data()
    print("数据生成完成！")
