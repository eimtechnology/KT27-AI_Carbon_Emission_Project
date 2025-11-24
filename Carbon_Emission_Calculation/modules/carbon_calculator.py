# -*- coding: utf-8 -*-
"""
食物碳排放计算模块
Food Carbon Emission Calculation Module

提供完整的食物碳排放因子数据库和计算功能
Provides comprehensive food carbon emission factor database and calculation functions

参考数据来源 Reference Data Sources:
- FAO (Food and Agriculture Organization)
- IPCC (Intergovernmental Panel on Climate Change)
- EPA (Environmental Protection Agency)
- 中国生命周期基础数据库 China Life Cycle Database
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EmissionFactor:
    """
    排放因子数据类
    Emission Factor Data Class
    """
    food_name_zh: str          # 中文名称
    food_name_en: str          # 英文名称
    category: str              # 食物类别
    emission_factor: float     # 碳排放因子 (kg CO2e / kg)
    unit: str                  # 单位
    source: str                # 数据来源
    confidence: float          # 数据可信度 (0-1)
    notes: str = ""            # 备注
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'food_name_zh': self.food_name_zh,
            'food_name_en': self.food_name_en,
            'category': self.category,
            'emission_factor': self.emission_factor,
            'unit': self.unit,
            'source': self.source,
            'confidence': self.confidence,
            'notes': self.notes
        }


class CarbonEmissionDatabase:
    """
    碳排放因子数据库
    Carbon Emission Factor Database
    """
    
    def __init__(self):
        """初始化数据库"""
        self.emission_factors = {}
        self.categories = set()
        self._init_database()
    
    def _init_database(self):
        """
        初始化完整的食物碳排放因子数据库
        Initialize comprehensive food carbon emission factor database
        """
        
        # 肉类 Meat Products
        meat_factors = [
            EmissionFactor("牛肉", "Beef", "肉类", 60.0, "kg", "FAO", 0.95, "红肉，高排放"),
            EmissionFactor("羊肉", "Lamb", "肉类", 39.2, "kg", "FAO", 0.9, "红肉，高排放"),
            EmissionFactor("猪肉", "Pork", "肉类", 12.1, "kg", "FAO", 0.9, "白肉，中等排放"),
            EmissionFactor("鸡肉", "Chicken", "肉类", 6.9, "kg", "FAO", 0.9, "白肉，较低排放"),
            EmissionFactor("鸭肉", "Duck", "肉类", 8.5, "kg", "FAO", 0.85, "家禽类"),
            EmissionFactor("火鸡", "Turkey", "肉类", 10.9, "kg", "FAO", 0.85, "家禽类"),
            EmissionFactor("兔肉", "Rabbit", "肉类", 4.3, "kg", "FAO", 0.8, "小型哺乳动物"),
            EmissionFactor("鹿肉", "Venison", "肉类", 8.1, "kg", "FAO", 0.75, "野生动物"),
        ]
        
        # 海鲜类 Seafood
        seafood_factors = [
            EmissionFactor("三文鱼", "Salmon", "海鲜", 11.9, "kg", "FAO", 0.9, "养殖鱼类"),
            EmissionFactor("金枪鱼", "Tuna", "海鲜", 9.7, "kg", "FAO", 0.85, "海洋鱼类"),
            EmissionFactor("鳕鱼", "Cod", "海鲜", 2.3, "kg", "FAO", 0.85, "白鱼"),
            EmissionFactor("虾", "Shrimp", "海鲜", 18.2, "kg", "FAO", 0.8, "甲壳类，高排放"),
            EmissionFactor("龙虾", "Lobster", "海鲜", 22.0, "kg", "FAO", 0.8, "甲壳类，高排放"),
            EmissionFactor("蟹", "Crab", "海鲜", 15.4, "kg", "FAO", 0.8, "甲壳类"),
            EmissionFactor("贻贝", "Mussels", "海鲜", 1.6, "kg", "FAO", 0.85, "贝类，低排放"),
            EmissionFactor("扇贝", "Scallops", "海鲜", 2.9, "kg", "FAO", 0.8, "贝类"),
            EmissionFactor("鲷鱼", "Sea Bream", "海鲜", 5.1, "kg", "FAO", 0.8, "养殖鱼类"),
            EmissionFactor("带鱼", "Hairtail", "海鲜", 3.8, "kg", "中国数据库", 0.8, "海洋鱼类"),
        ]
        
        # 乳制品 Dairy Products
        dairy_factors = [
            EmissionFactor("牛奶", "Milk", "乳制品", 3.2, "kg", "FAO", 0.95, "液体乳制品"),
            EmissionFactor("奶酪", "Cheese", "乳制品", 21.2, "kg", "FAO", 0.9, "硬质奶酪"),
            EmissionFactor("黄油", "Butter", "乳制品", 23.8, "kg", "FAO", 0.9, "动物脂肪"),
            EmissionFactor("酸奶", "Yogurt", "乳制品", 2.2, "kg", "FAO", 0.85, "发酵乳制品"),
            EmissionFactor("奶油", "Cream", "乳制品", 14.3, "kg", "FAO", 0.85, "高脂乳制品"),
            EmissionFactor("冰淇淋", "Ice Cream", "乳制品", 6.8, "kg", "EPA", 0.8, "冷冻甜品"),
        ]
        
        # 蛋类 Eggs
        egg_factors = [
            EmissionFactor("鸡蛋", "Chicken Eggs", "蛋类", 4.2, "kg", "FAO", 0.9, "家禽蛋类"),
            EmissionFactor("鸭蛋", "Duck Eggs", "蛋类", 4.8, "kg", "中国数据库", 0.8, "水禽蛋类"),
            EmissionFactor("鹅蛋", "Goose Eggs", "蛋类", 5.2, "kg", "中国数据库", 0.75, "大型蛋类"),
            EmissionFactor("鹌鹑蛋", "Quail Eggs", "蛋类", 3.9, "kg", "中国数据库", 0.75, "小型蛋类"),
        ]
        
        # 谷物类 Grains & Cereals
        grain_factors = [
            EmissionFactor("大米", "Rice", "谷物", 4.0, "kg", "FAO", 0.9, "主要粮食，甲烷排放"),
            EmissionFactor("小麦", "Wheat", "谷物", 1.4, "kg", "FAO", 0.9, "主要粮食"),
            EmissionFactor("玉米", "Corn", "谷物", 1.1, "kg", "FAO", 0.9, "饲料谷物"),
            EmissionFactor("燕麦", "Oats", "谷物", 0.9, "kg", "FAO", 0.85, "营养谷物"),
            EmissionFactor("大麦", "Barley", "谷物", 1.2, "kg", "FAO", 0.85, "饲料谷物"),
            EmissionFactor("高粱", "Sorghum", "谷物", 1.0, "kg", "FAO", 0.8, "抗旱谷物"),
            EmissionFactor("小米", "Millet", "谷物", 0.7, "kg", "中国数据库", 0.8, "传统谷物"),
            EmissionFactor("藜麦", "Quinoa", "谷物", 2.3, "kg", "EPA", 0.8, "超级食物"),
        ]
        
        # 豆类 Legumes
        legume_factors = [
            EmissionFactor("大豆", "Soybeans", "豆类", 1.2, "kg", "FAO", 0.9, "蛋白豆类"),
            EmissionFactor("黑豆", "Black Beans", "豆类", 0.8, "kg", "FAO", 0.85, "蛋白豆类"),
            EmissionFactor("红豆", "Red Beans", "豆类", 0.9, "kg", "中国数据库", 0.8, "传统豆类"),
            EmissionFactor("绿豆", "Mung Beans", "豆类", 0.7, "kg", "中国数据库", 0.8, "夏季豆类"),
            EmissionFactor("豌豆", "Peas", "豆类", 0.9, "kg", "FAO", 0.85, "蛋白豆类"),
            EmissionFactor("扁豆", "Lentils", "豆类", 0.9, "kg", "FAO", 0.85, "蛋白豆类"),
            EmissionFactor("鹰嘴豆", "Chickpeas", "豆类", 0.8, "kg", "FAO", 0.8, "中东豆类"),
        ]
        
        # 蔬菜类 Vegetables
        vegetable_factors = [
            EmissionFactor("土豆", "Potatoes", "蔬菜", 0.5, "kg", "FAO", 0.9, "根茎类"),
            EmissionFactor("红薯", "Sweet Potatoes", "蔬菜", 0.3, "kg", "FAO", 0.85, "根茎类"),
            EmissionFactor("胡萝卜", "Carrots", "蔬菜", 0.4, "kg", "FAO", 0.85, "根茎类"),
            EmissionFactor("白萝卜", "Daikon Radish", "蔬菜", 0.3, "kg", "中国数据库", 0.8, "根茎类"),
            EmissionFactor("洋葱", "Onions", "蔬菜", 0.4, "kg", "FAO", 0.85, "鳞茎类"),
            EmissionFactor("大蒜", "Garlic", "蔬菜", 0.6, "kg", "FAO", 0.8, "鳞茎类"),
            EmissionFactor("白菜", "Chinese Cabbage", "蔬菜", 0.4, "kg", "中国数据库", 0.85, "叶菜类"),
            EmissionFactor("卷心菜", "Cabbage", "蔬菜", 0.5, "kg", "FAO", 0.85, "叶菜类"),
            EmissionFactor("菠菜", "Spinach", "蔬菜", 2.0, "kg", "FAO", 0.8, "叶菜类，温室种植"),
            EmissionFactor("生菜", "Lettuce", "蔬菜", 1.3, "kg", "FAO", 0.8, "叶菜类"),
            EmissionFactor("西红柿", "Tomatoes", "蔬菜", 2.1, "kg", "FAO", 0.85, "果菜类，温室"),
            EmissionFactor("黄瓜", "Cucumbers", "蔬菜", 1.1, "kg", "FAO", 0.8, "果菜类"),
            EmissionFactor("茄子", "Eggplant", "蔬菜", 0.7, "kg", "中国数据库", 0.8, "果菜类"),
            EmissionFactor("青椒", "Bell Peppers", "蔬菜", 1.3, "kg", "FAO", 0.8, "果菜类"),
            EmissionFactor("辣椒", "Chili Peppers", "蔬菜", 1.0, "kg", "中国数据库", 0.75, "调味蔬菜"),
            EmissionFactor("西兰花", "Broccoli", "蔬菜", 2.0, "kg", "FAO", 0.8, "十字花科"),
            EmissionFactor("花椰菜", "Cauliflower", "蔬菜", 1.9, "kg", "FAO", 0.8, "十字花科"),
            EmissionFactor("芹菜", "Celery", "蔬菜", 1.4, "kg", "FAO", 0.75, "茎菜类"),
            EmissionFactor("韭菜", "Chinese Chives", "蔬菜", 0.8, "kg", "中国数据库", 0.75, "香料蔬菜"),
        ]
        
        # 水果类 Fruits
        fruit_factors = [
            EmissionFactor("苹果", "Apples", "水果", 0.6, "kg", "FAO", 0.9, "温带水果"),
            EmissionFactor("香蕉", "Bananas", "水果", 0.7, "kg", "FAO", 0.9, "热带水果"),
            EmissionFactor("橙子", "Oranges", "水果", 0.4, "kg", "FAO", 0.85, "柑橘类"),
            EmissionFactor("柠檬", "Lemons", "水果", 0.5, "kg", "FAO", 0.8, "柑橘类"),
            EmissionFactor("葡萄", "Grapes", "水果", 1.8, "kg", "FAO", 0.8, "浆果类"),
            EmissionFactor("草莓", "Strawberries", "水果", 1.4, "kg", "FAO", 0.75, "浆果类"),
            EmissionFactor("蓝莓", "Blueberries", "水果", 2.3, "kg", "EPA", 0.75, "浆果类"),
            EmissionFactor("桃子", "Peaches", "水果", 0.8, "kg", "FAO", 0.8, "核果类"),
            EmissionFactor("梨", "Pears", "水果", 0.5, "kg", "FAO", 0.8, "仁果类"),
            EmissionFactor("樱桃", "Cherries", "水果", 1.7, "kg", "FAO", 0.75, "核果类"),
            EmissionFactor("西瓜", "Watermelon", "水果", 0.4, "kg", "中国数据库", 0.8, "瓜类"),
            EmissionFactor("哈密瓜", "Cantaloupe", "水果", 0.5, "kg", "中国数据库", 0.75, "瓜类"),
            EmissionFactor("猕猴桃", "Kiwi", "水果", 1.1, "kg", "FAO", 0.75, "热带水果"),
            EmissionFactor("芒果", "Mango", "水果", 0.8, "kg", "FAO", 0.8, "热带水果"),
            EmissionFactor("菠萝", "Pineapple", "水果", 0.5, "kg", "FAO", 0.8, "热带水果"),
            EmissionFactor("荔枝", "Lychee", "水果", 1.2, "kg", "中国数据库", 0.75, "热带水果"),
            EmissionFactor("龙眼", "Longan", "水果", 1.0, "kg", "中国数据库", 0.75, "热带水果"),
        ]
        
        # 坚果类 Nuts
        nut_factors = [
            EmissionFactor("杏仁", "Almonds", "坚果", 13.5, "kg", "EPA", 0.8, "树坚果，高水需求"),
            EmissionFactor("核桃", "Walnuts", "坚果", 7.0, "kg", "EPA", 0.8, "树坚果"),
            EmissionFactor("花生", "Peanuts", "坚果", 2.5, "kg", "FAO", 0.85, "地下坚果"),
            EmissionFactor("腰果", "Cashews", "坚果", 14.3, "kg", "EPA", 0.75, "热带坚果"),
            EmissionFactor("开心果", "Pistachios", "坚果", 8.5, "kg", "EPA", 0.75, "树坚果"),
            EmissionFactor("榛子", "Hazelnuts", "坚果", 5.1, "kg", "EPA", 0.75, "树坚果"),
            EmissionFactor("巴西坚果", "Brazil Nuts", "坚果", 3.2, "kg", "EPA", 0.7, "野生坚果"),
            EmissionFactor("松子", "Pine Nuts", "坚果", 12.0, "kg", "中国数据库", 0.7, "针叶坚果"),
        ]
        
        # 加工食品 Processed Foods
        processed_factors = [
            EmissionFactor("面包", "Bread", "加工食品", 1.6, "kg", "EPA", 0.85, "烘焙食品"),
            EmissionFactor("面条", "Noodles", "加工食品", 2.2, "kg", "中国数据库", 0.8, "面制品"),
            EmissionFactor("饼干", "Cookies", "加工食品", 3.8, "kg", "EPA", 0.75, "烘焙零食"),
            EmissionFactor("蛋糕", "Cake", "加工食品", 4.5, "kg", "EPA", 0.75, "烘焙甜品"),
            EmissionFactor("巧克力", "Chocolate", "加工食品", 18.7, "kg", "EPA", 0.8, "可可制品"),
            EmissionFactor("糖果", "Candy", "加工食品", 2.8, "kg", "EPA", 0.7, "糖制品"),
            EmissionFactor("薯片", "Potato Chips", "加工食品", 5.6, "kg", "EPA", 0.75, "油炸零食"),
            EmissionFactor("方便面", "Instant Noodles", "加工食品", 6.5, "kg", "中国数据库", 0.75, "快餐食品"),
        ]
        
        # 饮料类 Beverages
        beverage_factors = [
            EmissionFactor("咖啡", "Coffee", "饮料", 17.0, "kg", "FAO", 0.85, "热带作物"),
            EmissionFactor("茶叶", "Tea", "饮料", 5.3, "kg", "FAO", 0.8, "热带作物"),
            EmissionFactor("果汁", "Fruit Juice", "饮料", 1.2, "kg", "EPA", 0.75, "加工饮料"),
            EmissionFactor("可乐", "Cola", "饮料", 0.8, "kg", "EPA", 0.75, "碳酸饮料"),
            EmissionFactor("啤酒", "Beer", "饮料", 1.3, "kg", "EPA", 0.8, "酒精饮料"),
            EmissionFactor("红酒", "Wine", "饮料", 2.4, "kg", "EPA", 0.8, "酒精饮料"),
            EmissionFactor("豆浆", "Soy Milk", "饮料", 0.9, "kg", "中国数据库", 0.8, "植物奶"),
        ]
        
        # 食用油 Cooking Oils
        oil_factors = [
            EmissionFactor("橄榄油", "Olive Oil", "食用油", 3.2, "kg", "EPA", 0.8, "植物油"),
            EmissionFactor("菜籽油", "Rapeseed Oil", "食用油", 2.8, "kg", "EPA", 0.85, "植物油"),
            EmissionFactor("大豆油", "Soybean Oil", "食用油", 3.0, "kg", "EPA", 0.85, "植物油"),
            EmissionFactor("花生油", "Peanut Oil", "食用油", 3.5, "kg", "中国数据库", 0.8, "植物油"),
            EmissionFactor("玉米油", "Corn Oil", "食用油", 2.9, "kg", "EPA", 0.8, "植物油"),
            EmissionFactor("葵花籽油", "Sunflower Oil", "食用油", 3.1, "kg", "EPA", 0.8, "植物油"),
            EmissionFactor("芝麻油", "Sesame Oil", "食用油", 4.2, "kg", "中国数据库", 0.75, "调味油"),
        ]
        
        # 调料香料 Seasonings & Spices
        spice_factors = [
            EmissionFactor("盐", "Salt", "调料", 0.3, "kg", "EPA", 0.9, "矿物调料"),
            EmissionFactor("糖", "Sugar", "调料", 1.8, "kg", "FAO", 0.85, "甜味调料"),
            EmissionFactor("胡椒", "Black Pepper", "调料", 8.5, "kg", "FAO", 0.7, "香料"),
            EmissionFactor("八角", "Star Anise", "调料", 6.2, "kg", "中国数据库", 0.7, "中式香料"),
            EmissionFactor("桂皮", "Cinnamon", "调料", 7.8, "kg", "FAO", 0.7, "树皮香料"),
            EmissionFactor("丁香", "Cloves", "调料", 12.5, "kg", "FAO", 0.7, "花蕾香料"),
            EmissionFactor("生姜", "Ginger", "调料", 2.1, "kg", "FAO", 0.8, "根茎调料"),
            EmissionFactor("大蒜粉", "Garlic Powder", "调料", 3.8, "kg", "EPA", 0.75, "加工调料"),
        ]
        
        # 整合所有数据
        all_factors = (
            meat_factors + seafood_factors + dairy_factors + egg_factors +
            grain_factors + legume_factors + vegetable_factors + fruit_factors +
            nut_factors + processed_factors + beverage_factors + oil_factors +
            spice_factors
        )
        
        # 添加到数据库
        for factor in all_factors:
            # 使用中英文名称作为键
            self.emission_factors[factor.food_name_zh] = factor
            self.emission_factors[factor.food_name_en.lower()] = factor
            self.categories.add(factor.category)
        
        print(f"已加载 {len(all_factors)} 种食物的碳排放因子")
        print(f"包含 {len(self.categories)} 个类别")
    
    def get_emission_factor(self, food_name: str) -> Optional[EmissionFactor]:
        """
        获取食物的排放因子
        Get emission factor for a food item
        
        Args:
            food_name (str): 食物名称（中文或英文）
            
        Returns:
            Optional[EmissionFactor]: 排放因子对象
        """
        # 直接匹配
        if food_name in self.emission_factors:
            return self.emission_factors[food_name]
        
        # 小写匹配
        if food_name.lower() in self.emission_factors:
            return self.emission_factors[food_name.lower()]
        
        # 模糊匹配
        return self._fuzzy_match(food_name)
    
    def _fuzzy_match(self, food_name: str) -> Optional[EmissionFactor]:
        """
        模糊匹配食物名称
        Fuzzy match food name
        
        Args:
            food_name (str): 食物名称
            
        Returns:
            Optional[EmissionFactor]: 匹配的排放因子
        """
        food_name_lower = food_name.lower()
        
        # 检查是否包含关键词
        for key, factor in self.emission_factors.items():
            if isinstance(key, str):
                # 中文匹配
                if food_name in factor.food_name_zh:
                    return factor
                
                # 英文匹配
                if food_name_lower in factor.food_name_en.lower():
                    return factor
                
                # 反向匹配
                if factor.food_name_zh in food_name:
                    return factor
                
                if factor.food_name_en.lower() in food_name_lower:
                    return factor
        
        return None
    
    def get_category_factors(self, category: str) -> List[EmissionFactor]:
        """
        获取特定类别的所有排放因子
        Get all emission factors for a specific category
        
        Args:
            category (str): 类别名称
            
        Returns:
            List[EmissionFactor]: 排放因子列表
        """
        factors = []
        seen_foods = set()
        
        for factor in self.emission_factors.values():
            if (factor.category == category and 
                factor.food_name_zh not in seen_foods):
                factors.append(factor)
                seen_foods.add(factor.food_name_zh)
        
        return factors
    
    def search_foods(self, keyword: str) -> List[EmissionFactor]:
        """
        搜索包含关键词的食物
        Search foods containing keyword
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            List[EmissionFactor]: 匹配的食物列表
        """
        results = []
        seen_foods = set()
        keyword_lower = keyword.lower()
        
        for factor in self.emission_factors.values():
            if factor.food_name_zh not in seen_foods:
                if (keyword in factor.food_name_zh or 
                    keyword_lower in factor.food_name_en.lower() or
                    keyword in factor.category):
                    results.append(factor)
                    seen_foods.add(factor.food_name_zh)
        
        return results


class CarbonCalculator:
    """
    碳排放计算器
    Carbon Emission Calculator
    """
    
    def __init__(self):
        """初始化计算器"""
        self.database = CarbonEmissionDatabase()
        self.default_factor = 2.5  # 默认排放因子 kg CO2e/kg
        
        # 单位转换因子
        self.unit_conversions = {
            'kg': 1.0,
            'g': 0.001,
            'lb': 0.453592,
            'oz': 0.0283495,
            'ton': 1000.0,
            '斤': 0.5,
            '两': 0.05
        }
    
    def calculate_emission(
        self, 
        food_name: str, 
        weight: float, 
        weight_unit: str = 'g'
    ) -> Dict:
        """
        计算食物的碳排放
        Calculate carbon emission for food
        
        Args:
            food_name (str): 食物名称
            weight (float): 重量
            weight_unit (str): 重量单位
            
        Returns:
            Dict: 计算结果
        """
        # 转换重量为公斤
        weight_kg = self._convert_weight(weight, weight_unit)
        
        if weight_kg is None:
            return {
                'error': f'不支持的重量单位: {weight_unit}',
                'supported_units': list(self.unit_conversions.keys())
            }
        
        # 获取排放因子
        emission_factor = self.database.get_emission_factor(food_name)
        
        if emission_factor is None:
            # 使用默认因子
            total_emission = weight_kg * self.default_factor
            result = {
                'food_name': food_name,
                'weight_kg': weight_kg,
                'emission_factor': self.default_factor,
                'total_emission_kg': total_emission,
                'confidence': 0.3,
                'source': '默认估值',
                'category': '未知',
                'warning': '未找到准确的排放因子，使用默认值'
            }
        else:
            # 使用数据库因子
            total_emission = weight_kg * emission_factor.emission_factor
            result = {
                'food_name_zh': emission_factor.food_name_zh,
                'food_name_en': emission_factor.food_name_en,
                'weight_kg': weight_kg,
                'emission_factor': emission_factor.emission_factor,
                'total_emission_kg': total_emission,
                'confidence': emission_factor.confidence,
                'source': emission_factor.source,
                'category': emission_factor.category,
                'notes': emission_factor.notes
            }
        
        # 添加环境影响对比
        result.update(self._get_environmental_impact(total_emission))
        
        return result
    
    def _convert_weight(self, weight: float, unit: str) -> Optional[float]:
        """
        转换重量单位为公斤
        Convert weight to kilograms
        
        Args:
            weight (float): 重量值
            unit (str): 重量单位
            
        Returns:
            Optional[float]: 转换后的重量（公斤）
        """
        if unit in self.unit_conversions:
            return weight * self.unit_conversions[unit]
        return None
    
    def _get_environmental_impact(self, emission_kg: float) -> Dict:
        """
        获取环境影响对比
        Get environmental impact comparisons
        
        Args:
            emission_kg (float): 碳排放量（公斤）
            
        Returns:
            Dict: 环境影响对比数据
        """
        # 环境影响对比数据
        comparisons = {}
        
        # 汽车行驶距离对比 (假设每公里0.2kg CO2)
        car_km = emission_kg / 0.2
        comparisons['equivalent_car_km'] = round(car_km, 2)
        
        # 电力消耗对比 (假设每度电0.6kg CO2)
        electricity_kwh = emission_kg / 0.6
        comparisons['equivalent_electricity_kwh'] = round(electricity_kwh, 2)
        
        # 树木吸收对比 (一棵树年吸收约22kg CO2)
        trees_yearly = emission_kg / 22.0
        comparisons['equivalent_trees_yearly'] = round(trees_yearly, 4)
        
        # 手机充电次数对比 (每次充电约0.0084kg CO2)
        phone_charges = emission_kg / 0.0084
        comparisons['equivalent_phone_charges'] = round(phone_charges, 1)
        
        # 塑料袋对比 (每个塑料袋约0.006kg CO2)
        plastic_bags = emission_kg / 0.006
        comparisons['equivalent_plastic_bags'] = round(plastic_bags, 1)
        
        return comparisons
    
    def calculate_meal_emission(self, meal_items: List[Dict]) -> Dict:
        """
        计算整餐的碳排放
        Calculate carbon emission for an entire meal
        
        Args:
            meal_items (List[Dict]): 餐食项目列表
                格式: [{'name': '食物名', 'weight': 重量, 'unit': '单位'}, ...]
                
        Returns:
            Dict: 整餐排放计算结果
        """
        total_emission = 0.0
        total_weight = 0.0
        item_results = []
        categories = set()
        
        for item in meal_items:
            result = self.calculate_emission(
                item['name'],
                item['weight'],
                item.get('unit', 'g')
            )
            
            if 'error' not in result:
                total_emission += result['total_emission_kg']
                total_weight += result['weight_kg']
                categories.add(result.get('category', '未知'))
                item_results.append(result)
        
        # 计算平均置信度
        if item_results:
            avg_confidence = sum(r['confidence'] for r in item_results) / len(item_results)
        else:
            avg_confidence = 0.0
        
        meal_result = {
            'total_emission_kg': total_emission,
            'total_weight_kg': total_weight,
            'item_count': len(item_results),
            'categories': list(categories),
            'average_confidence': avg_confidence,
            'item_details': item_results
        }
        
        # 添加环境影响对比
        meal_result.update(self._get_environmental_impact(total_emission))
        
        return meal_result
    
    def get_emission_trends(self, food_name: str, days: int = 7) -> Dict:
        """
        获取食物排放趋势分析
        Get emission trend analysis for a food item
        
        Args:
            food_name (str): 食物名称
            days (int): 分析天数
            
        Returns:
            Dict: 趋势分析结果
        """
        emission_factor = self.database.get_emission_factor(food_name)
        
        if emission_factor is None:
            return {'error': f'未找到食物: {food_name}'}
        
        # 生成模拟趋势数据（实际应用中应从数据库获取）
        import random
        base_factor = emission_factor.emission_factor
        
        trends = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            # 添加随机波动 (±5%)
            factor_variation = base_factor * (1 + random.uniform(-0.05, 0.05))
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'emission_factor': round(factor_variation, 3),
                'relative_change': round((factor_variation - base_factor) / base_factor * 100, 2)
            })
        
        return {
            'food_name': emission_factor.food_name_zh,
            'base_factor': base_factor,
            'trends': trends,
            'analysis': {
                'min_factor': min(t['emission_factor'] for t in trends),
                'max_factor': max(t['emission_factor'] for t in trends),
                'avg_factor': sum(t['emission_factor'] for t in trends) / len(trends),
                'volatility': max(abs(t['relative_change']) for t in trends)
            }
        }
    
    def compare_foods(self, food_list: List[str], weight: float = 100, unit: str = 'g') -> Dict:
        """
        比较多种食物的碳排放
        Compare carbon emissions of multiple foods
        
        Args:
            food_list (List[str]): 食物名称列表
            weight (float): 比较重量
            unit (str): 重量单位
            
        Returns:
            Dict: 比较结果
        """
        comparisons = []
        
        for food_name in food_list:
            result = self.calculate_emission(food_name, weight, unit)
            if 'error' not in result:
                comparisons.append({
                    'food_name': result.get('food_name_zh', food_name),
                    'emission_factor': result['emission_factor'],
                    'total_emission': result['total_emission_kg'],
                    'category': result.get('category', '未知'),
                    'confidence': result['confidence']
                })
        
        if not comparisons:
            return {'error': '没有找到有效的食物数据'}
        
        # 排序
        comparisons.sort(key=lambda x: x['total_emission'])
        
        # 计算相对比较
        min_emission = comparisons[0]['total_emission']
        for comp in comparisons:
            comp['relative_impact'] = round(comp['total_emission'] / min_emission, 2)
        
        return {
            'comparison_weight': f"{weight} {unit}",
            'food_count': len(comparisons),
            'results': comparisons,
            'summary': {
                'lowest_emission': comparisons[0],
                'highest_emission': comparisons[-1],
                'emission_range': comparisons[-1]['total_emission'] - comparisons[0]['total_emission']
            }
        }
    
    def get_category_statistics(self) -> Dict:
        """
        获取各类别的统计信息
        Get statistics for each food category
        
        Returns:
            Dict: 类别统计信息
        """
        category_stats = {}
        
        for category in self.database.categories:
            factors = self.database.get_category_factors(category)
            
            if factors:
                emissions = [f.emission_factor for f in factors]
                category_stats[category] = {
                    'food_count': len(factors),
                    'min_emission': min(emissions),
                    'max_emission': max(emissions),
                    'avg_emission': sum(emissions) / len(emissions),
                    'median_emission': sorted(emissions)[len(emissions)//2]
                }
        
        return category_stats
    
    def suggest_alternatives(self, food_name: str, max_suggestions: int = 5) -> Dict:
        """
        推荐低碳替代食物
        Suggest low-carbon alternative foods
        
        Args:
            food_name (str): 原食物名称
            max_suggestions (int): 最大推荐数量
            
        Returns:
            Dict: 推荐结果
        """
        original_factor = self.database.get_emission_factor(food_name)
        
        if original_factor is None:
            return {'error': f'未找到食物: {food_name}'}
        
        # 获取同类别的食物
        same_category = self.database.get_category_factors(original_factor.category)
        
        # 筛选出排放更低的食物
        alternatives = [
            f for f in same_category 
            if f.emission_factor < original_factor.emission_factor
            and f.food_name_zh != original_factor.food_name_zh
        ]
        
        # 按排放因子排序
        alternatives.sort(key=lambda x: x.emission_factor)
        
        # 限制数量
        alternatives = alternatives[:max_suggestions]
        
        suggestions = []
        for alt in alternatives:
            emission_reduction = original_factor.emission_factor - alt.emission_factor
            reduction_percentage = (emission_reduction / original_factor.emission_factor) * 100
            
            suggestions.append({
                'food_name': alt.food_name_zh,
                'emission_factor': alt.emission_factor,
                'emission_reduction': round(emission_reduction, 2),
                'reduction_percentage': round(reduction_percentage, 1),
                'confidence': alt.confidence
            })
        
        return {
            'original_food': original_factor.food_name_zh,
            'original_emission': original_factor.emission_factor,
            'alternatives': suggestions,
            'category': original_factor.category
        } 