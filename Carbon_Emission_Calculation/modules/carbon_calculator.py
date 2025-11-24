# -*- coding: utf-8 -*-
"""
Food Carbon Emission Calculation Module

Provides comprehensive food carbon emission factor database and calculation functions.

Reference Data Sources:
- FAO (Food and Agriculture Organization)
- IPCC (Intergovernmental Panel on Climate Change)
- EPA (Environmental Protection Agency)
- Life Cycle Database
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class EmissionFactor:
    """
    Emission Factor Data Class
    """
    food_name: str             # English Name
    category: str              # Category
    emission_factor: float     # Carbon Emission Factor (kg CO2e / kg)
    unit: str                  # Unit
    source: str                # Data Source
    confidence: float          # Data Confidence (0-1)
    notes: str = ""            # Notes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            'food_name': self.food_name,
            'category': self.category,
            'emission_factor': self.emission_factor,
            'unit': self.unit,
            'source': self.source,
            'confidence': self.confidence,
            'notes': self.notes
        }


class CarbonEmissionDatabase:
    """
    Carbon Emission Factor Database
    """
    
    def __init__(self):
        """Initialize database"""
        self.emission_factors = {}
        self.categories = set()
        self._init_database()
    
    def _init_database(self):
        """
        Initialize comprehensive food carbon emission factor database
        """
        
        # Meat Products
        meat_factors = [
            EmissionFactor("Beef", "Meat", 60.0, "kg", "FAO", 0.95, "Red meat, high emission"),
            EmissionFactor("Lamb", "Meat", 39.2, "kg", "FAO", 0.9, "Red meat, high emission"),
            EmissionFactor("Pork", "Meat", 12.1, "kg", "FAO", 0.9, "White meat, medium emission"),
            EmissionFactor("Chicken", "Meat", 6.9, "kg", "FAO", 0.9, "White meat, lower emission"),
            EmissionFactor("Duck", "Meat", 8.5, "kg", "FAO", 0.85, "Poultry"),
            EmissionFactor("Turkey", "Meat", 10.9, "kg", "FAO", 0.85, "Poultry"),
            EmissionFactor("Rabbit", "Meat", 4.3, "kg", "FAO", 0.8, "Small mammal"),
            EmissionFactor("Venison", "Meat", 8.1, "kg", "FAO", 0.75, "Game meat"),
        ]
        
        # Seafood
        seafood_factors = [
            EmissionFactor("Salmon", "Seafood", 11.9, "kg", "FAO", 0.9, "Farmed fish"),
            EmissionFactor("Tuna", "Seafood", 9.7, "kg", "FAO", 0.85, "Marine fish"),
            EmissionFactor("Cod", "Seafood", 2.3, "kg", "FAO", 0.85, "White fish"),
            EmissionFactor("Shrimp", "Seafood", 18.2, "kg", "FAO", 0.8, "Crustaceans, high emission"),
            EmissionFactor("Lobster", "Seafood", 22.0, "kg", "FAO", 0.8, "Crustaceans, high emission"),
            EmissionFactor("Crab", "Seafood", 15.4, "kg", "FAO", 0.8, "Crustaceans"),
            EmissionFactor("Mussels", "Seafood", 1.6, "kg", "FAO", 0.85, "Shellfish, low emission"),
            EmissionFactor("Scallops", "Seafood", 2.9, "kg", "FAO", 0.8, "Shellfish"),
            EmissionFactor("Sea Bream", "Seafood", 5.1, "kg", "FAO", 0.8, "Farmed fish"),
            EmissionFactor("Hairtail", "Seafood", 3.8, "kg", "Database", 0.8, "Marine fish"),
        ]
        
        # Dairy Products
        dairy_factors = [
            EmissionFactor("Milk", "Dairy", 3.2, "kg", "FAO", 0.95, "Liquid dairy"),
            EmissionFactor("Cheese", "Dairy", 21.2, "kg", "FAO", 0.9, "Hard cheese"),
            EmissionFactor("Butter", "Dairy", 23.8, "kg", "FAO", 0.9, "Animal fat"),
            EmissionFactor("Yogurt", "Dairy", 2.2, "kg", "FAO", 0.85, "Fermented dairy"),
            EmissionFactor("Cream", "Dairy", 14.3, "kg", "FAO", 0.85, "High fat dairy"),
            EmissionFactor("Ice Cream", "Dairy", 6.8, "kg", "EPA", 0.8, "Frozen dessert"),
        ]
        
        # Eggs
        egg_factors = [
            EmissionFactor("Eggs", "Eggs", 4.2, "kg", "FAO", 0.9, "Poultry eggs"),
            EmissionFactor("Duck Eggs", "Eggs", 4.8, "kg", "Database", 0.8, "Waterfowl eggs"),
            EmissionFactor("Goose Eggs", "Eggs", 5.2, "kg", "Database", 0.75, "Large eggs"),
            EmissionFactor("Quail Eggs", "Eggs", 3.9, "kg", "Database", 0.75, "Small eggs"),
        ]
        
        # Grains & Cereals
        grain_factors = [
            EmissionFactor("Rice", "Grains", 4.0, "kg", "FAO", 0.9, "Staple, methane emission"),
            EmissionFactor("Wheat", "Grains", 1.4, "kg", "FAO", 0.9, "Staple"),
            EmissionFactor("Corn", "Grains", 1.1, "kg", "FAO", 0.9, "Feed grain"),
            EmissionFactor("Oats", "Grains", 0.9, "kg", "FAO", 0.85, "Nutritious grain"),
            EmissionFactor("Barley", "Grains", 1.2, "kg", "FAO", 0.85, "Feed grain"),
            EmissionFactor("Sorghum", "Grains", 1.0, "kg", "FAO", 0.8, "Drought resistant"),
            EmissionFactor("Millet", "Grains", 0.7, "kg", "Database", 0.8, "Traditional grain"),
            EmissionFactor("Quinoa", "Grains", 2.3, "kg", "EPA", 0.8, "Superfood"),
        ]
        
        # Legumes
        legume_factors = [
            EmissionFactor("Soybeans", "Legumes", 1.2, "kg", "FAO", 0.9, "Protein legume"),
            EmissionFactor("Black Beans", "Legumes", 0.8, "kg", "FAO", 0.85, "Protein legume"),
            EmissionFactor("Red Beans", "Legumes", 0.9, "kg", "Database", 0.8, "Traditional legume"),
            EmissionFactor("Mung Beans", "Legumes", 0.7, "kg", "Database", 0.8, "Summer legume"),
            EmissionFactor("Peas", "Legumes", 0.9, "kg", "FAO", 0.85, "Protein legume"),
            EmissionFactor("Lentils", "Legumes", 0.9, "kg", "FAO", 0.85, "Protein legume"),
            EmissionFactor("Chickpeas", "Legumes", 0.8, "kg", "FAO", 0.8, "Middle eastern legume"),
        ]
        
        # Vegetables
        vegetable_factors = [
            EmissionFactor("Potatoes", "Vegetables", 0.5, "kg", "FAO", 0.9, "Root vegetable"),
            EmissionFactor("Sweet Potatoes", "Vegetables", 0.3, "kg", "FAO", 0.85, "Root vegetable"),
            EmissionFactor("Carrots", "Vegetables", 0.4, "kg", "FAO", 0.85, "Root vegetable"),
            EmissionFactor("Radish", "Vegetables", 0.3, "kg", "Database", 0.8, "Root vegetable"),
            EmissionFactor("Onions", "Vegetables", 0.4, "kg", "FAO", 0.85, "Bulb vegetable"),
            EmissionFactor("Garlic", "Vegetables", 0.6, "kg", "FAO", 0.8, "Bulb vegetable"),
            EmissionFactor("Cabbage", "Vegetables", 0.5, "kg", "FAO", 0.85, "Leafy vegetable"),
            EmissionFactor("Spinach", "Vegetables", 2.0, "kg", "FAO", 0.8, "Leafy vegetable, greenhouse"),
            EmissionFactor("Lettuce", "Vegetables", 1.3, "kg", "FAO", 0.8, "Leafy vegetable"),
            EmissionFactor("Tomatoes", "Vegetables", 2.1, "kg", "FAO", 0.85, "Fruit vegetable, greenhouse"),
            EmissionFactor("Cucumbers", "Vegetables", 1.1, "kg", "FAO", 0.8, "Fruit vegetable"),
            EmissionFactor("Eggplant", "Vegetables", 0.7, "kg", "Database", 0.8, "Fruit vegetable"),
            EmissionFactor("Bell Peppers", "Vegetables", 1.3, "kg", "FAO", 0.8, "Fruit vegetable"),
            EmissionFactor("Broccoli", "Vegetables", 2.0, "kg", "FAO", 0.8, "Cruciferous"),
            EmissionFactor("Cauliflower", "Vegetables", 1.9, "kg", "FAO", 0.8, "Cruciferous"),
            EmissionFactor("Celery", "Vegetables", 1.4, "kg", "FAO", 0.75, "Stem vegetable"),
        ]
        
        # Fruits
        fruit_factors = [
            EmissionFactor("Apples", "Fruits", 0.6, "kg", "FAO", 0.9, "Temperate fruit"),
            EmissionFactor("Bananas", "Fruits", 0.7, "kg", "FAO", 0.9, "Tropical fruit"),
            EmissionFactor("Oranges", "Fruits", 0.4, "kg", "FAO", 0.85, "Citrus"),
            EmissionFactor("Lemons", "Fruits", 0.5, "kg", "FAO", 0.8, "Citrus"),
            EmissionFactor("Grapes", "Fruits", 1.8, "kg", "FAO", 0.8, "Berries"),
            EmissionFactor("Strawberries", "Fruits", 1.4, "kg", "FAO", 0.75, "Berries"),
            EmissionFactor("Blueberries", "Fruits", 2.3, "kg", "EPA", 0.75, "Berries"),
            EmissionFactor("Peaches", "Fruits", 0.8, "kg", "FAO", 0.8, "Stone fruit"),
            EmissionFactor("Pears", "Fruits", 0.5, "kg", "FAO", 0.8, "Pome fruit"),
            EmissionFactor("Cherries", "Fruits", 1.7, "kg", "FAO", 0.75, "Stone fruit"),
            EmissionFactor("Watermelon", "Fruits", 0.4, "kg", "Database", 0.8, "Melon"),
            EmissionFactor("Kiwi", "Fruits", 1.1, "kg", "FAO", 0.75, "Tropical fruit"),
            EmissionFactor("Mango", "Fruits", 0.8, "kg", "FAO", 0.8, "Tropical fruit"),
            EmissionFactor("Pineapple", "Fruits", 0.5, "kg", "FAO", 0.8, "Tropical fruit"),
        ]
        
        # Nuts
        nut_factors = [
            EmissionFactor("Almonds", "Nuts", 13.5, "kg", "EPA", 0.8, "Tree nut, high water use"),
            EmissionFactor("Walnuts", "Nuts", 7.0, "kg", "EPA", 0.8, "Tree nut"),
            EmissionFactor("Peanuts", "Nuts", 2.5, "kg", "FAO", 0.85, "Ground nut"),
            EmissionFactor("Cashews", "Nuts", 14.3, "kg", "EPA", 0.75, "Tropical nut"),
            EmissionFactor("Pistachios", "Nuts", 8.5, "kg", "EPA", 0.75, "Tree nut"),
            EmissionFactor("Hazelnuts", "Nuts", 5.1, "kg", "EPA", 0.75, "Tree nut"),
        ]
        
        # Processed Foods
        processed_factors = [
            EmissionFactor("Bread", "Processed", 1.6, "kg", "EPA", 0.85, "Bakery"),
            EmissionFactor("Noodles", "Processed", 2.2, "kg", "Database", 0.8, "Pasta"),
            EmissionFactor("Cookies", "Processed", 3.8, "kg", "EPA", 0.75, "Bakery snack"),
            EmissionFactor("Cake", "Processed", 4.5, "kg", "EPA", 0.75, "Dessert"),
            EmissionFactor("Chocolate", "Processed", 18.7, "kg", "EPA", 0.8, "Cocoa product"),
            EmissionFactor("Candy", "Processed", 2.8, "kg", "EPA", 0.7, "Confectionery"),
            EmissionFactor("Potato Chips", "Processed", 5.6, "kg", "EPA", 0.75, "Fried snack"),
            EmissionFactor("Instant Noodles", "Processed", 6.5, "kg", "Database", 0.75, "Fast food"),
        ]
        
        # Beverages
        beverage_factors = [
            EmissionFactor("Coffee", "Beverages", 17.0, "kg", "FAO", 0.85, "Tropical crop"),
            EmissionFactor("Tea", "Beverages", 5.3, "kg", "FAO", 0.8, "Tropical crop"),
            EmissionFactor("Fruit Juice", "Beverages", 1.2, "kg", "EPA", 0.75, "Processed drink"),
            EmissionFactor("Cola", "Beverages", 0.8, "kg", "EPA", 0.75, "Carbonated drink"),
            EmissionFactor("Beer", "Beverages", 1.3, "kg", "EPA", 0.8, "Alcoholic drink"),
            EmissionFactor("Wine", "Beverages", 2.4, "kg", "EPA", 0.8, "Alcoholic drink"),
            EmissionFactor("Soy Milk", "Beverages", 0.9, "kg", "Database", 0.8, "Plant milk"),
        ]
        
        # Cooking Oils
        oil_factors = [
            EmissionFactor("Olive Oil", "Oils", 3.2, "kg", "EPA", 0.8, "Vegetable oil"),
            EmissionFactor("Rapeseed Oil", "Oils", 2.8, "kg", "EPA", 0.85, "Vegetable oil"),
            EmissionFactor("Soybean Oil", "Oils", 3.0, "kg", "EPA", 0.85, "Vegetable oil"),
            EmissionFactor("Peanut Oil", "Oils", 3.5, "kg", "Database", 0.8, "Vegetable oil"),
            EmissionFactor("Corn Oil", "Oils", 2.9, "kg", "EPA", 0.8, "Vegetable oil"),
            EmissionFactor("Sunflower Oil", "Oils", 3.1, "kg", "EPA", 0.8, "Vegetable oil"),
            EmissionFactor("Sesame Oil", "Oils", 4.2, "kg", "Database", 0.75, "Seasoning oil"),
        ]
        
        # Seasonings & Spices
        spice_factors = [
            EmissionFactor("Salt", "Seasoning", 0.3, "kg", "EPA", 0.9, "Mineral"),
            EmissionFactor("Sugar", "Seasoning", 1.8, "kg", "FAO", 0.85, "Sweetener"),
            EmissionFactor("Black Pepper", "Seasoning", 8.5, "kg", "FAO", 0.7, "Spice"),
            EmissionFactor("Ginger", "Seasoning", 2.1, "kg", "FAO", 0.8, "Root spice"),
            EmissionFactor("Garlic Powder", "Seasoning", 3.8, "kg", "EPA", 0.75, "Processed spice"),
        ]
        
        # Combine all data
        all_factors = (
            meat_factors + seafood_factors + dairy_factors + egg_factors +
            grain_factors + legume_factors + vegetable_factors + fruit_factors +
            nut_factors + processed_factors + beverage_factors + oil_factors +
            spice_factors
        )
        
        # Add to database
        for factor in all_factors:
            self.emission_factors[factor.food_name.lower()] = factor
            self.categories.add(factor.category)
        
        print(f"Loaded {len(all_factors)} food carbon emission factors")
        print(f"Covering {len(self.categories)} categories")
    
    def get_emission_factor(self, food_name: str) -> Optional[EmissionFactor]:
        """
        Get emission factor for a food item
        
        Args:
            food_name (str): Food name
            
        Returns:
            Optional[EmissionFactor]: Emission factor object
        """
        # Direct match (lowercase)
        if food_name.lower() in self.emission_factors:
            return self.emission_factors[food_name.lower()]
        
        # Fuzzy match
        return self._fuzzy_match(food_name)
    
    def _fuzzy_match(self, food_name: str) -> Optional[EmissionFactor]:
        """
        Fuzzy match food name
        
        Args:
            food_name (str): Food name
            
        Returns:
            Optional[EmissionFactor]: Matched emission factor
        """
        food_name_lower = food_name.lower()
        
        # Check if contains keywords
        for key, factor in self.emission_factors.items():
            # Forward match
            if food_name_lower in key:
                return factor
            
            # Reverse match
            if key in food_name_lower:
                return factor
        
        return None
    
    def get_category_factors(self, category: str) -> List[EmissionFactor]:
        """
        Get all emission factors for a specific category
        
        Args:
            category (str): Category name
            
        Returns:
            List[EmissionFactor]: List of emission factors
        """
        factors = []
        
        for factor in self.emission_factors.values():
            if factor.category == category:
                factors.append(factor)
        
        return factors


class CarbonCalculator:
    """
    Carbon Emission Calculator
    """
    
    def __init__(self):
        """Initialize calculator"""
        self.database = CarbonEmissionDatabase()
        self.default_factor = 2.5  # Default emission factor kg CO2e/kg
        
        # Unit conversion factors
        self.unit_conversions = {
            'kg': 1.0,
            'g': 0.001,
            'lb': 0.453592,
            'oz': 0.0283495,
            'ton': 1000.0
        }
    
    def calculate_emission(
        self, 
        food_name: str, 
        weight: float, 
        weight_unit: str = 'g'
    ) -> Dict:
        """
        Calculate carbon emission for food
        
        Args:
            food_name (str): Food name
            weight (float): Weight
            weight_unit (str): Weight unit
            
        Returns:
            Dict: Calculation result
        """
        # Convert weight to kg
        weight_kg = self._convert_weight(weight, weight_unit)
        
        if weight_kg is None:
            return {
                'error': f'Unsupported weight unit: {weight_unit}',
                'supported_units': list(self.unit_conversions.keys())
            }
        
        # Get emission factor
        emission_factor = self.database.get_emission_factor(food_name)
        
        if emission_factor is None:
            # Use default factor
            total_emission = weight_kg * self.default_factor
            result = {
                'food_name': food_name,
                'weight_kg': weight_kg,
                'emission_factor': self.default_factor,
                'total_co2_kg': total_emission,  # Renamed to match GUI expectation
                'confidence': 0.3,
                'source': 'Default Estimate',
                'category': 'Unknown',
                'in_database': False,
                'impact_level': self._get_impact_level(total_emission)
            }
        else:
            # Use database factor
            total_emission = weight_kg * emission_factor.emission_factor
            result = {
                'food_name': emission_factor.food_name,
                'weight_kg': weight_kg,
                'emission_factor': emission_factor.emission_factor,
                'total_co2_kg': total_emission,  # Renamed to match GUI expectation
                'confidence': emission_factor.confidence,
                'source': emission_factor.source,
                'category': emission_factor.category,
                'notes': emission_factor.notes,
                'in_database': True,
                'impact_level': self._get_impact_level(total_emission)
            }
        
        # Add environmental comparisons
        result.update(self._get_environmental_impact(total_emission))
        
        return result
    
    def _convert_weight(self, weight: float, unit: str) -> Optional[float]:
        """Convert weight to kilograms"""
        if unit in self.unit_conversions:
            return weight * self.unit_conversions[unit]
        return None
        
    def _get_impact_level(self, co2_kg: float) -> str:
        """Determine impact level based on CO2 emission"""
        if co2_kg < 0.1:
            return "LOW"
        elif co2_kg < 0.5:
            return "MEDIUM"
        elif co2_kg < 2.0:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _get_environmental_impact(self, emission_kg: float) -> Dict:
        """
        Get environmental impact comparisons
        
        Args:
            emission_kg (float): Carbon emission (kg)
            
        Returns:
            Dict: Impact comparison data
        """
        comparisons = {}
        
        # Car driving comparison (assuming 0.2kg CO2 per km)
        car_km = emission_kg / 0.2
        comparisons['car_km_equivalent'] = round(car_km, 2)
        
        # Tree absorption comparison (assuming 22kg CO2 per year per tree)
        trees_yearly = emission_kg / (22.0 / 12.0) # Monthly absorption
        comparisons['tree_months_equivalent'] = round(trees_yearly, 1)
        
        # Phone charging comparison (approx 0.0084kg CO2 per charge)
        phone_charges = emission_kg / 0.0084
        comparisons['phone_charges_equivalent'] = round(phone_charges, 0)
        
        return comparisons
