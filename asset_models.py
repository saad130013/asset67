import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class AssetAnalyzer:
    def __init__(self, df):
        self.df = df
        self.clean_data()
    
    def clean_data(self):
        """تنظيف البيانات الأساسية"""
        try:
            # تحويل التواريخ
            date_columns = ['Date Placed in Service']
            for col in date_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            # تحويل الأرقام
            numeric_columns = ['Cost', 'Depreciation amount', 'Net Book Value', 'Useful Life', 'Quantity']
            for col in numeric_columns:
                if col in self.df.columns:
                    # إزالة أي رموز غير رقمية وتحويل إلى أرقام
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # تنظيف النصوص
            text_columns = ['Asset Description', 'Custodian', 'City', 'Level 1 FA Module - English Description']
            for col in text_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip()
            
            st.success("✅ تم تنظيف البيانات بنجاح")
            
        except Exception as e:
            st.error(f"❌ خطأ في تنظيف البيانات: {str(e)}")
    
    def get_summary_stats(self):
        """إحصائيات ملخصة"""
        try:
            total_assets = len(self.df)
            total_cost = self.df['Cost'].sum() if 'Cost' in self.df.columns else 0
            total_depreciation = self.df['Depreciation amount'].sum() if 'Depreciation amount' in self.df.columns else 0
            total_net_value = self.df['Net Book Value'].sum() if 'Net Book Value' in self.df.columns else 0
            
            # متوسط التكلفة لكل أصل
            avg_cost = total_cost / total_assets if total_assets > 0 else 0
            
            # نسبة الإهلاك الإجمالية
            depreciation_rate = (total_depreciation / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_assets': total_assets,
                'total_cost': total_cost,
                'total_depreciation': total_depreciation,
                'total_net_value': total_net_value,
                'avg_cost': avg_cost,
                'depreciation_rate': depreciation_rate
            }
        except Exception as e:
            st.error(f"❌ خطأ في حساب الإحصائيات: {str(e)}")
            return {}
    
    def get_assets_by_category(self):
        """الأصول حسب التصنيف"""
        try:
            if 'Level 1 FA Module - English Description' in self.df.columns:
                category_data = self.df.groupby('Level 1 FA Module - English Description').agg({
                    'Cost': 'sum',
                    'Net Book Value': 'sum',
                    'Depreciation amount': 'sum',
                    'Tag number': 'count'
                }).rename(columns={'Tag number': 'Count'}).round(2)
                
                # إضافة نسبة الإهلاك لكل فئة
                category_data['Depreciation_Rate'] = (category_data['Depreciation amount'] / category_data['Cost'] * 100).round(2)
                
                return category_data.sort_values('Cost', ascending=False)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تحليل التصنيفات: {str(e)}")
            return pd.DataFrame()
    
    def get_assets_by_location(self):
        """الأصول حسب الموقع"""
        try:
            if 'City' in self.df.columns:
                location_data = self.df.groupby('City').agg({
                    'Cost': 'sum',
                    'Net Book Value': 'sum',
                    'Depreciation amount': 'sum',
                    'Tag number': 'count'
                }).rename(columns={'Tag number': 'Count'}).round(2)
                
                # إضافة نسبة التكلفة لكل موقع
                total_cost = location_data['Cost'].sum()
                location_data['Cost_Percentage'] = (location_data['Cost'] / total_cost * 100).round(2)
                
                return location_data.sort_values('Cost', ascending=False)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تحليل المواقع: {str(e)}")
            return pd.DataFrame()
    
    def get_assets_by_custodian(self):
        """الأصول حسب القسم المسؤول"""
        try:
            if 'Custodian' in self.df.columns:
                custodian_data = self.df.groupby('Custodian').agg({
                    'Cost': 'sum',
                    'Net Book Value': 'sum',
                    'Depreciation amount': 'sum',
                    'Tag number': 'count'
                }).rename(columns={'Tag number': 'Count'}).round(2)
                
                return custodian_data.sort_values('Cost', ascending=False).head(10)  # أهم 10 أقسام
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تحليل الأقسام: {str(e)}")
            return pd.DataFrame()
    
    def get_depreciation_analysis(self):
        """تحليل الإهلاك"""
        try:
            # حساب عمر الأصل
            current_year = pd.Timestamp.now().year
            if 'Date Placed in Service' in self.df.columns:
                self.df['Asset_Age'] = current_year - pd.to_datetime(self.df['Date Placed in Service']).dt.year
            else:
                self.df['Asset_Age'] = 0
            
            # حساب نسبة الإهلاك
            if 'Cost' in self.df.columns and 'Depreciation amount' in self.df.columns:
                self.df['Depreciation_Rate'] = (self.df['Depreciation amount'] / self.df['Cost'] * 100).round(2)
                
                # تصنيف حالة الأصل
                conditions = [
                    self.df['Depreciation_Rate'] >= 80,
                    self.df['Depreciation_Rate'] >= 50,
                    self.df['Depreciation_Rate'] >= 20,
                    self.df['Depreciation_Rate'] > 0
                ]
                choices = ['قديم', 'متوسط', 'جديد', 'جديد جداً']
                self.df['Asset_Condition'] = np.select(conditions, choices, default='لم يبدأ الإهلاك')
            
            return self.df[['Asset Description', 'Custodian', 'Cost', 'Depreciation amount', 
                          'Net Book Value', 'Depreciation_Rate', 'Asset_Age', 'Asset_Condition']]
        except Exception as e:
            st.error(f"❌ خطأ في تحليل الإهلاك: {str(e)}")
            return pd.DataFrame()
    
    def get_assets_by_year(self):
        """الأصول حسب سنة التشغيل"""
        try:
            if 'Date Placed in Service' in self.df.columns:
                self.df['Service_Year'] = pd.to_datetime(self.df['Date Placed in Service']).dt.year
                year_data = self.df.groupby('Service_Year').agg({
                    'Cost': 'sum',
                    'Net Book Value': 'sum',
                    'Tag number': 'count'
                }).rename(columns={'Tag number': 'Count'}).round(2)
                
                return year_data.sort_index()
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تحليل السنوات: {str(e)}")
            return pd.DataFrame()
    
    def get_high_value_assets(self, threshold=10000):
        """الأصول عالية القيمة"""
        try:
            if 'Cost' in self.df.columns:
                high_value = self.df[self.df['Cost'] >= threshold].sort_values('Cost', ascending=False)
                return high_value[['Asset Description', 'Custodian', 'Cost', 'Net Book Value', 'Depreciation amount']]
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تصفية الأصول عالية القيمة: {str(e)}")
            return pd.DataFrame()
    
    def get_fully_depreciated_assets(self):
        """الأصول المتهالكة بالكامل"""
        try:
            if 'Depreciation amount' in self.df.columns and 'Cost' in self.df.columns:
                fully_depreciated = self.df[self.df['Depreciation amount'] >= self.df['Cost']]
                return fully_depreciated[['Asset Description', 'Custodian', 'Cost', 'Depreciation amount', 'Net Book Value']]
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تصفية الأصول المتهالكة: {str(e)}")
            return pd.DataFrame()
    
    def search_assets(self, search_term):
        """بحث في الأصول"""
        try:
            if not search_term:
                return pd.DataFrame()
            
            search_columns = ['Asset Description', 'Custodian', 'City', 'Tag number', 
                            'Level 1 FA Module - English Description', 'Manufacturer']
            
            mask = pd.Series(False, index=self.df.index)
            
            for col in search_columns:
                if col in self.df.columns:
                    # البحث بأحرف صغيرة للتقليل من حساسية الحالة
                    mask |= self.df[col].astype(str).str.lower().str.contains(
                        search_term.lower(), na=False
                    )
            
            results = self.df[mask]
            
            # إذا لم توجد نتائج، حاول البحث بكلمات جزئية
            if len(results) == 0:
                for col in search_columns:
                    if col in self.df.columns:
                        words = search_term.lower().split()
                        for word in words:
                            if len(word) > 2:  # تجاهل الكلمات القصيرة جداً
                                mask |= self.df[col].astype(str).str.lower().str.contains(word, na=False)
                
                results = self.df[mask]
            
            return results
        except Exception as e:
            st.error(f"❌ خطأ في البحث: {str(e)}")
            return pd.DataFrame()
    
    def get_asset_details(self, tag_number):
        """الحصول على تفاصيل أصل محدد"""
        try:
            if 'Tag number' in self.df.columns:
                asset = self.df[self.df['Tag number'] == tag_number]
                if not asset.empty:
                    return asset.iloc[0]
            return None
        except Exception as e:
            st.error(f"❌ خطأ في جلب تفاصيل الأصل: {str(e)}")
            return None
    
    def generate_asset_report(self):
        """تقرير شامل عن الأصول"""
        try:
            report = {
                'summary': self.get_summary_stats(),
                'by_category': self.get_assets_by_category(),
                'by_location': self.get_assets_by_location(),
                'by_custodian': self.get_assets_by_custodian(),
                'depreciation_analysis': self.get_depreciation_analysis(),
                'high_value_assets': self.get_high_value_assets(),
                'fully_depreciated': self.get_fully_depreciated_assets()
            }
            return report
        except Exception as e:
            st.error(f"❌ خطأ في إنشاء التقرير: {str(e)}")
            return {}
    
    def get_manufacturer_analysis(self):
        """تحليل الأصول حسب الشركة المصنعة"""
        try:
            if 'Manufacturer' in self.df.columns:
                manufacturer_data = self.df.groupby('Manufacturer').agg({
                    'Cost': 'sum',
                    'Net Book Value': 'sum',
                    'Tag number': 'count',
                    'Depreciation amount': 'sum'
                }).rename(columns={'Tag number': 'Count'}).round(2)
                
                # إضافة متوسط التكلفة
                manufacturer_data['Avg_Cost'] = (manufacturer_data['Cost'] / manufacturer_data['Count']).round(2)
                
                return manufacturer_data.sort_values('Cost', ascending=False)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ خطأ في تحليل الشركات المصنعة: {str(e)}")
            return pd.DataFrame()

class AssetPredictor:
    """فئة للتنبؤ بقيم الأصول (للإصدارات المستقبلية)"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.df = analyzer.df
    
    def predict_depreciation(self, months=12):
        """تنبؤ بقيم الإهلاك المستقبلية"""
        try:
            # هذا نموذج مبسط للتنبؤ - يمكن تطويره لاحقاً
            predictions = []
            
            for _, asset in self.df.iterrows():
                if 'Cost' in asset and 'Depreciation amount' in asset and 'Useful Life' in asset:
                    cost = asset['Cost']
                    current_dep = asset['Depreciation amount']
                    useful_life = asset['Useful Life'] if pd.notna(asset['Useful Life']) else 3
                    
                    # حساب الإهلاك الشهري
                    monthly_dep = cost / (useful_life * 12) if useful_life > 0 else 0
                    
                    # التنبؤ بالقيمة المستقبلية
                    future_dep = current_dep + (monthly_dep * months)
                    future_net_value = max(0, cost - future_dep)
                    
                    predictions.append({
                        'Tag number': asset.get('Tag number', ''),
                        'Asset Description': asset.get('Asset Description', ''),
                        'Current_Net_Value': asset.get('Net Book Value', 0),
                        'Future_Net_Value': future_net_value,
                        'Depreciation_Increase': future_dep - current_dep,
                        'Months': months
                    })
            
            return pd.DataFrame(predictions)
        except Exception as e:
            st.error(f"❌ خطأ في التنبؤ بالإهلاك: {str(e)}")
            return pd.DataFrame()

# دالة مساعدة للتحقق من جودة البيانات
def validate_data_quality(df):
    """التحقق من جودة البيانات"""
    issues = []
    
    # التحقق من القيم المفقودة
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        issues.append(f"بيانات مفقودة: {missing_data[missing_data > 0].to_dict()}")
    
    # التحقق من التكاليف السلبية
    if 'Cost' in df.columns:
        negative_costs = df[df['Cost'] < 0]
        if len(negative_costs) > 0:
            issues.append(f"تكاليف سلبية: {len(negative_costs)} سجل")
    
    # التحقق من الإهلاك الزائد
    if 'Cost' in df.columns and 'Depreciation amount' in df.columns:
        excess_depreciation = df[df['Depreciation amount'] > df['Cost']]
        if len(excess_depreciation) > 0:
            issues.append(f"إهلاك زائد عن التكلفة: {len(excess_depreciation)} سجل")
    
    return issues
