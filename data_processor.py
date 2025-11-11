import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import re

class DataProcessor:
    def __init__(self):
        self.raw_df = None
        self.processed_df = None
        
    @staticmethod
    def load_data(file_path, sheet_name):
        """تحميل البيانات من ملف Excel"""
        try:
            # قراءة البيانات مع تخطي الصفوف الفارغة في البداية
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
            
            if df.empty:
                raise ValueError("الملف لا يحتوي على بيانات")
                
            st.success(f"✅ تم تحميل {len(df)} سجل بنجاح")
            return df
            
        except FileNotFoundError:
            st.error("❌ ملف البيانات غير موجود")
            raise
        except Exception as e:
            st.error(f"❌ خطأ في تحميل البيانات: {str(e)}")
            raise
    
    def preprocess_data(self, df):
        """معالجة مسبقة للبيانات"""
        try:
            self.raw_df = df.copy()
            
            # 1. تنظيف أسماء الأعمدة
            df = self.clean_column_names(df)
            
            # 2. إزالة الصفوف الفارغة تماماً
            df = self.remove_empty_rows(df)
            
            # 3. تنظيف أنواع البيانات
            df = self.clean_data_types(df)
            
            # 4. معالجة القيم المفقودة
            df = self.handle_missing_values(df)
            
            # 5. إضافة أعمدة محسوبة
            df = self.add_calculated_columns(df)
            
            # 6. التحقق من جودة البيانات
            self.validate_data_quality(df)
            
            self.processed_df = df
            st.success("✅ تم معالجة البيانات بنجاح")
            return df
            
        except Exception as e:
            st.error(f"❌ خطأ في معالجة البيانات: {str(e)}")
            raise
    
    def clean_column_names(self, df):
        """تنظيف أسماء الأعمدة"""
        try:
            # إزالة المسافات الزائدة ورموز خاصة
            df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
            
            # استبدال المسافات بنقاط سفلي للتعامل الأسهل
            clean_columns = {}
            for col in df.columns:
                clean_col = re.sub(r'[^\w\s]', '', col)  # إزالة الرموز الخاصة
                clean_col = re.sub(r'\s+', '_', clean_col.strip())  # استبدال المسافات
                clean_columns[col] = clean_col
            
            df = df.rename(columns=clean_columns)
            return df
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في تنظيف أسماء الأعمدة: {str(e)}")
            return df
    
    def remove_empty_rows(self, df):
        """إزالة الصفوف الفارغة تماماً"""
        try:
            # إزالة الصفوف التي تكون جميع قيمها فارغة
            initial_count = len(df)
            df = df.dropna(how='all')
            removed_count = initial_count - len(df)
            
            if removed_count > 0:
                st.info(f"📊 تم إزالة {removed_count} صف فارغ")
                
            return df
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في إزالة الصفوف الفارغة: {str(e)}")
            return df
    
    def clean_data_types(self, df):
        """تنظيف أنواع البيانات"""
        try:
            # تحويل التواريخ
            date_columns = ['Date_Placed_in_Service', 'تاريخ الدخول في الخدمة']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                    # إذا فشل التحويل، حاول بصيغ أخرى
                    if df[col].isna().all():
                        df[col] = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d %H:%M:%S')
            
            # تحويل الأعمدة الرقمية
            numeric_columns = [
                'Cost', 'التكلفة', 
                'Depreciation_amount', 'قسط الاهلاك',
                'Net_Book_Value', 'القيمة الدفترية',
                'Useful_Life', 'العمر الإنتاجي',
                'Quantity', 'العدد',
                'Residual_Value', 'القيمة المتبقية في نهاية العمر',
                'Accumulated_Depreciation', 'الاستهلاك المتراكم'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    # تنظيف النصوص قبل التحويل
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                    
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # تنظيف الأعمدة النصية
            text_columns = [
                'Asset_Description', 'وصف الأصل',
                'Custodian', 'القسم أو الإدارة المسؤولة', 
                'City', 'المدينة',
                'Level_1_FA_Module_English_Description', 'وصف تصنيف الأصول المستوى الأول - انجليزي',
                'Manufacturer', 'المصنع',
                'Tag_number', 'رقم البطاقة'
            ]
            
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    # استبدال 'Not Available' و 'N/A' بقيم فارغة
                    df[col] = df[col].replace(['Not Available', 'N/A', 'nan', 'None'], '')
            
            return df
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في تنظيف أنواع البيانات: {str(e)}")
            return df
    
    def handle_missing_values(self, df):
        """معالجة القيم المفقودة"""
        try:
            missing_report = {}
            
            for col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    missing_percentage = (missing_count / len(df)) * 100
                    missing_report[col] = {
                        'count': missing_count,
                        'percentage': round(missing_percentage, 2)
                    }
                    
                    # معالجة حسب نوع العمود
                    if col in ['Cost', 'Depreciation_amount', 'Net_Book_Value']:
                        df[col] = df[col].fillna(0)
                    elif col in ['Asset_Description', 'Custodian']:
                        df[col] = df[col].fillna('غير محدد')
                    elif 'Date' in col:
                        # ترك التواريخ الفارغة كما هي
                        pass
            
            if missing_report:
                st.warning("⚠️ يوجد قيم مفقودة في البيانات")
                for col, info in missing_report.items():
                    if info['percentage'] > 5:  # فقط إذا كانت النسبة كبيرة
                        st.write(f"   - {col}: {info['count']} قيم مفقودة ({info['percentage']}%)")
            
            return df
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في معالجة القيم المفقودة: {str(e)}")
            return df
    
    def add_calculated_columns(self, df):
        """إضافة أعمدة محسوبة"""
        try:
            # حساب عمر الأصل (بالسنوات)
            if 'Date_Placed_in_Service' in df.columns:
                current_date = pd.Timestamp.now()
                df['Asset_Age_Years'] = ((current_date - pd.to_datetime(df['Date_Placed_in_Service'])) / np.timedelta64(1, 'Y')).round(1)
            
            # حساب نسبة الإهلاك
            if 'Cost' in df.columns and 'Depreciation_amount' in df.columns:
                df['Depreciation_Rate'] = (df['Depreciation_amount'] / df['Cost'] * 100).round(2)
                # معالجة القيم غير المنطقية
                df['Depreciation_Rate'] = df['Depreciation_Rate'].clip(0, 100)
            
            # تصنيف حالة الأصل
            if 'Depreciation_Rate' in df.columns:
                conditions = [
                    df['Depreciation_Rate'] >= 80,
                    df['Depreciation_Rate'] >= 50,
                    df['Depreciation_Rate'] >= 20,
                    df['Depreciation_Rate'] > 0
                ]
                choices = ['قديم', 'متوسط', 'جديد', 'جديد جداً']
                df['Asset_Condition'] = np.select(conditions, choices, default='لم يبدأ الإهلاك')
            
            # تصنيف قيمة الأصل
            if 'Cost' in df.columns:
                conditions = [
                    df['Cost'] >= 10000,
                    df['Cost'] >= 5000,
                    df['Cost'] >= 1000
                ]
                choices = ['عالية', 'متوسطة', 'منخفضة']
                df['Value_Category'] = np.select(conditions, choices, default='very_low')
            
            # حساب العمر المتبقي
            if 'Useful_Life' in df.columns and 'Asset_Age_Years' in df.columns:
                df['Remaining_Life'] = (df['Useful_Life'] - df['Asset_Age_Years']).round(1)
                df['Remaining_Life'] = df['Remaining_Life'].clip(0)  # لا تسمح بقيم سالبة
            
            # إضافة سنة التشغيل
            if 'Date_Placed_in_Service' in df.columns:
                df['Service_Year'] = pd.to_datetime(df['Date_Placed_in_Service']).dt.year
            
            st.info("📈 تم إضافة الأعمدة المحسوبة بنجاح")
            return df
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في إضافة الأعمدة المحسوبة: {str(e)}")
            return df
    
    def validate_data_quality(self, df):
        """التحقق من جودة البيانات"""
        try:
            issues = []
            
            # 1. التحقق من التكاليف السلبية
            if 'Cost' in df.columns:
                negative_costs = df[df['Cost'] < 0]
                if len(negative_costs) > 0:
                    issues.append(f"❌ تكاليف سلبية: {len(negative_costs)} سجل")
            
            # 2. التحقق من الإهلاك الزائد
            if 'Cost' in df.columns and 'Depreciation_amount' in df.columns:
                excess_depreciation = df[df['Depreciation_amount'] > df['Cost']]
                if len(excess_depreciation) > 0:
                    issues.append(f"❌ إهلاك زائد عن التكلفة: {len(excess_depreciation)} سجل")
            
            # 3. التحقق من القيم الدفترية السلبية
            if 'Net_Book_Value' in df.columns:
                negative_nbv = df[df['Net_Book_Value'] < 0]
                if len(negative_nbv) > 0:
                    issues.append(f"❌ قيم دفترية سلبية: {len(negative_nbv)} سجل")
            
            # 4. التحقق من الأعمار غير المنطقية
            if 'Asset_Age_Years' in df.columns:
                negative_age = df[df['Asset_Age_Years'] < 0]
                if len(negative_age) > 0:
                    issues.append(f"❌ أعمار سلبية: {len(negative_age)} سجل")
            
            # 5. التحقق من التكرار
            if 'Tag_number' in df.columns:
                duplicates = df[df.duplicated('Tag_number', keep=False)]
                if len(duplicates) > 0:
                    issues.append(f"❌ أرقام بطاقات مكررة: {len(duplicates)} سجل")
            
            if issues:
                st.warning("⚠️ مشاكل في جودة البيانات:")
                for issue in issues:
                    st.write(f"   {issue}")
            else:
                st.success("✅ جودة البيانات ممتازة")
                
            return issues
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في التحقق من جودة البيانات: {str(e)}")
            return []
    
    def get_data_summary(self, df):
        """الحصول على ملخص للبيانات"""
        try:
            summary = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'data_types': df.dtypes.value_counts().to_dict(),
                'date_range': None,
                'cost_range': None
            }
            
            # نطاق التواريخ
            if 'Date_Placed_in_Service' in df.columns:
                date_col = pd.to_datetime(df['Date_Placed_in_Service'])
                summary['date_range'] = {
                    'min': date_col.min(),
                    'max': date_col.max()
                }
            
            # نطاق التكاليف
            if 'Cost' in df.columns:
                summary['cost_range'] = {
                    'min': df['Cost'].min(),
                    'max': df['Cost'].max(),
                    'total': df['Cost'].sum()
                }
            
            return summary
            
        except Exception as e:
            st.warning(f"⚠️ تحذير في إنشاء ملخص البيانات: {str(e)}")
            return {}
    
    def export_processed_data(self, df, file_path):
        """تصدير البيانات المعالجة"""
        try:
            df.to_excel(file_path, index=False)
            st.success(f"✅ تم تصدير البيانات إلى {file_path}")
            return True
        except Exception as e:
            st.error(f"❌ خطأ في تصدير البيانات: {str(e)}")
            return False
    
    def filter_data(self, df, filters):
        """تصفية البيانات حسب معايير محددة"""
        try:
            filtered_df = df.copy()
            
            for column, value in filters.items():
                if value and column in filtered_df.columns:
                    if isinstance(value, (int, float)):
                        filtered_df = filtered_df[filtered_df[column] == value]
                    else:
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), case=False, na=False)]
            
            return filtered_df
            
        except Exception as e:
            st.error(f"❌ خطأ في تصفية البيانات: {str(e)}")
            return df

class DataValidator:
    """فئة للتحقق من صحة البيانات"""
    
    @staticmethod
    def validate_asset_data(df):
        """التحقق من صحة بيانات الأصول"""
        validation_results = {
            'passed': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # التحقق من الحقول الأساسية
            required_columns = ['Cost', 'Asset_Description', 'Tag_number']
            for col in required_columns:
                if col not in df.columns:
                    validation_results['errors'].append(f"العمود المطلوب '{col}' غير موجود")
            
            # التحقق من أرقام البطاقات الفريدة
            if 'Tag_number' in df.columns:
                duplicate_tags = df[df.duplicated('Tag_number', keep=False)]
                if len(duplicate_tags) > 0:
                    validation_results['warnings'].append(f"يوجد {len(duplicate_tags)} رقم بطاقة مكرر")
            
            # التحقق من القيم الرقمية
            numeric_columns = ['Cost', 'Depreciation_amount', 'Net_Book_Value']
            for col in numeric_columns:
                if col in df.columns:
                    if df[col].isna().any():
                        validation_results['warnings'].append(f"يوجد قيم مفقودة في {col}")
                    if (df[col] < 0).any():
                        validation_results['warnings'].append(f"يوجد قيم سلبية في {col}")
            
            if not validation_results['errors']:
                validation_results['passed'].append("جميع الاختبارات الأساسية نجحت")
            
            return validation_results
            
        except Exception as e:
            validation_results['errors'].append(f"خطأ في التحقق من البيانات: {str(e)}")
            return validation_results

# دوال مساعدة
def detect_data_patterns(df):
    """كشف أنماط البيانات"""
    patterns = {}
    
    try:
        # نمط التوزيع الزمني
        if 'Service_Year' in df.columns:
            yearly_pattern = df['Service_Year'].value_counts().sort_index()
            patterns['yearly_distribution'] = yearly_pattern.to_dict()
        
        # نمط التوزيع الجغرافي
        if 'City' in df.columns:
            city_pattern = df['City'].value_counts()
            patterns['city_distribution'] = city_pattern.to_dict()
        
        # نمط التصنيف
        if 'Level_1_FA_Module_English_Description' in df.columns:
            category_pattern = df['Level_1_FA_Module_English_Description'].value_counts()
            patterns['category_distribution'] = category_pattern.to_dict()
        
        return patterns
        
    except Exception as e:
        st.warning(f"⚠️ تحذير في كشف الأنماط: {str(e)}")
        return {}

def generate_data_report(df):
    """إنشاء تقرير شامل عن البيانات"""
    report = {
        'basic_info': {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # بالميجابايت
        },
        'data_quality': {},
        'patterns': detect_data_patterns(df)
    }
    
    return report
