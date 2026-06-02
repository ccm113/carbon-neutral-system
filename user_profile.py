import numpy as np
from config import SCORE_WEIGHTS

class UserProfile:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.profile = None
    
    def generate_profile(self):
        """生成用户低碳画像（垃圾分类数据可选）"""
        stats = self.data_processor.get_all_stats()
        
        # 检查各类数据是否存在
        has_garbage = bool(stats['garbage'])
        has_electricity = bool(stats['electricity'])
        has_transport = bool(stats['transport'])
        
        # 计算各项得分
        garbage_score = self._calculate_garbage_score(stats['garbage']) if has_garbage else None
        electricity_score = self._calculate_electricity_score(stats['electricity']) if has_electricity else None
        transport_score = self._calculate_transport_score(stats['transport']) if has_transport else None
        
        # 计算综合得分（根据可用数据调整权重）
        available_scores = []
        if garbage_score is not None:
            available_scores.append(('garbage', garbage_score))
        if electricity_score is not None:
            available_scores.append(('electricity', electricity_score))
        if transport_score is not None:
            available_scores.append(('transport', transport_score))
        
        if available_scores:
            # 可用数据平均权重
            weight = 1.0 / len(available_scores)
            total_score = sum(score * weight for _, score in available_scores)
        else:
            total_score = 0
        
        # 分析短板（只分析有数据的项）
        weaknesses = self._identify_weaknesses(garbage_score, electricity_score, transport_score)
        
        self.profile = {
            'garbage_score': garbage_score,
            'electricity_score': electricity_score,
            'transport_score': transport_score,
            'total_score': total_score,
            'weaknesses': weaknesses,
            'level': self._get_level(total_score),
            'stats': stats,
            'has_garbage': has_garbage,
            'has_electricity': has_electricity,
            'has_transport': has_transport
        }
        
        return self.profile
    
    def _calculate_garbage_score(self, garbage_stats):
        """计算垃圾分类得分（0-100）"""
        if not garbage_stats:
            return 50
        
        accuracy_rate = garbage_stats.get('accuracy_rate', 0)
        total_count = garbage_stats.get('total_count', 0)
        
        # 正确率得分（权重60%）
        accuracy_score = accuracy_rate * 60
        
        # 参与度得分（权重40%）- 根据投放频次
        frequency_score = min(total_count / 100 * 40, 40) if total_count > 0 else 0
        
        return round(accuracy_score + frequency_score, 1)
    
    def _calculate_electricity_score(self, electricity_stats):
        """计算用电得分（0-100）"""
        if not electricity_stats:
            return 50
        
        avg_daily = electricity_stats.get('avg_daily', 0)
        total_consumption = electricity_stats.get('total_consumption', 0)
        
        # 参考标准：普通家庭日均用电8-15 kWh
        # 用电量越少得分越高
        if avg_daily <= 8:
            consumption_score = 50
        elif avg_daily <= 12:
            consumption_score = 40 - (avg_daily - 8) * 2.5
        elif avg_daily <= 18:
            consumption_score = 30 - (avg_daily - 12) * 1.67
        else:
            consumption_score = max(0, 20 - (avg_daily - 18))
        
        # 时段得分：夜晚用电比例
        time_stats = electricity_stats.get('time_stats', {})
        total_by_time = time_stats.sum() if not time_stats.empty else 1
        night_ratio = time_stats.get('夜晚', 0) / total_by_time
        time_score = night_ratio * 30  # 夜晚用电比例越高越好（电价低）
        
        # 设备得分：空调使用控制
        device_stats = electricity_stats.get('device_stats', {})
        total_by_device = device_stats.sum() if not device_stats.empty else 1
        ac_ratio = device_stats.get('空调', 0) / total_by_device
        device_score = max(0, 20 - ac_ratio * 20)  # 空调用电越少得分越高
        
        return round(min(100, consumption_score + time_score + device_score), 1)
    
    def _calculate_transport_score(self, transport_stats):
        """计算出行得分（0-100）"""
        if not transport_stats:
            return 50
        
        green_ratio = transport_stats.get('green_ratio', 0)
        total_distance = transport_stats.get('total_distance', 0)
        
        # 绿色出行比例得分（权重70%）
        green_score = green_ratio * 70
        
        # 出行距离得分（权重30%）- 距离越短得分越高
        if total_distance <= 500:
            distance_score = 30
        elif total_distance <= 1000:
            distance_score = 25 - (total_distance - 500) * 0.01
        elif total_distance <= 2000:
            distance_score = 20 - (total_distance - 1000) * 0.005
        else:
            distance_score = max(0, 15 - (total_distance - 2000) * 0.002)
        
        return round(min(100, green_score + distance_score), 1)
    
    def _identify_weaknesses(self, garbage_score, electricity_score, transport_score):
        """识别碳排放短板（只分析有数据的项）"""
        weaknesses = []
        
        scores = {
            '垃圾分类': garbage_score,
            '用电习惯': electricity_score,
            '出行方式': transport_score
        }
        
        for category, score in scores.items():
            if score is None:
                continue  # 跳过没有数据的项
            if score < 40:
                weaknesses.append({'category': category, 'score': score, 'level': '严重短板', 'suggestion': self._get_weakness_suggestion(category)})
            elif score < 60:
                weaknesses.append({'category': category, 'score': score, 'level': '待改进', 'suggestion': self._get_weakness_suggestion(category)})
        
        # 按得分排序，优先显示得分最低的
        weaknesses.sort(key=lambda x: x['score'])
        
        return weaknesses
    
    def _get_weakness_suggestion(self, category):
        """获取短板改进建议"""
        suggestions = {
            '垃圾分类': '建议学习垃圾分类知识，使用分类指南，投放前仔细核对类别。',
            '用电习惯': '建议合理控制空调温度，使用节能电器，及时关闭待机设备。',
            '出行方式': '建议优先选择公共交通、步行或骑行，减少私家车使用频率。'
        }
        return suggestions.get(category, '')
    
    def _get_level(self, total_score):
        """根据综合得分确定低碳等级"""
        if total_score >= 85:
            return {'level': '低碳达人', 'color': 'green', 'description': '您的低碳生活表现优秀，继续保持！'}
        elif total_score >= 70:
            return {'level': '低碳践行者', 'color': 'blue', 'description': '您在低碳生活方面做得不错，还有提升空间。'}
        elif total_score >= 50:
            return {'level': '低碳学习者', 'color': 'yellow', 'description': '您正在学习低碳生活，继续努力！'}
        else:
            return {'level': '低碳新手', 'color': 'red', 'description': '建议您从基础开始，逐步养成低碳习惯。'}
    
    def get_profile_summary(self):
        """获取画像摘要文本"""
        if not self.profile:
            return ""
        
        p = self.profile
        summary = f"""用户低碳画像分析报告

【综合评分】{p['total_score']:.1f}分 - {p['level']['level']}
{p['level']['description']}

【分项得分】
"""
        
        # 只显示有数据的项
        if p['garbage_score'] is not None:
            summary += f"- 垃圾分类：{p['garbage_score']}分\n"
        else:
            summary += "- 垃圾分类：未提供数据\n"
        
        if p['electricity_score'] is not None:
            summary += f"- 用电习惯：{p['electricity_score']}分\n"
        else:
            summary += "- 用电习惯：未提供数据\n"
        
        if p['transport_score'] is not None:
            summary += f"- 出行方式：{p['transport_score']}分\n"
        else:
            summary += "- 出行方式：未提供数据\n"
        
        summary += "\n【碳排放短板】\n"
        if p['weaknesses']:
            for w in p['weaknesses']:
                summary += f"- {w['category']}：{w['level']}（{w['score']}分）\n  建议：{w['suggestion']}\n"
        else:
            summary += "暂无明显短板，继续保持！\n"
        
        summary += f"\n【碳排放统计】\n总碳排放量：{p['stats']['total_carbon']:.1f} kg CO2"
        
        return summary
