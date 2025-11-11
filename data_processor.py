# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import re

class DataProcessor:
    def __init__(self):
        self.raw_df = None
        self.processed_df = None

    # -------------------------------------------------
    # تحميل البيانات
    # -------------------------------------------------
    @staticmethod
    def load_data(file_path, sheet_name):
        """تحميل البيانات من ملف Excel"""
        try:
            # في كثير من ملفات FAR يكون أول صف هو عناوين عربية/إنجليزية مزدوجة
            # لذا نبدأ من السطر الثاني غالباً (header=1). عدّلها لو احتجت.
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

    # -------------------------------------------------
    # خط المعالجة الرئيسي
    # -------------------------------------------------
    def preprocess_data(self, df):
        """معالجة مسبقة للبيانات"""
        try:
            self.raw_df = df.copy()

            # 1) تنظيف أسماء الأعمدة
            df = self.clean_column_names(df)

            # 2) إزالة الصفوف الفارغة تماماً
            df = self.remove_empty_rows(df)

            # 3) تنظيف أنواع البيانات
            df = self.clean_data_types(df)

            # 4) معالجة القيم المفقودة
            df = self.handle_missing_values(df)

            # 5) إضافة أعمدة محسوبة (العمر، النسب، التصنيفات..)
            df = self.calculate_additional_metrics(df)

            # 6) التحقق من جودة البيانات
            self.validate_data_quality(df)

            self.processed_df = df
            st.success("✅ تم معالجة البيانات بنجاح")
            return df

        except Exception as e:
            st.error(f"❌ خطأ في معالجة البيانات: {str(e)}")
            raise

    # -------------------------------------------------
    # تنظيف أسماء الأعمدة
    # -------------------------------------------------
    def clean_column_names(self, df):
        """تنظيف أسماء الأعمدة (إزالة رموز/أسطر جديدة وتحويل المسافات إلى _)"""
        try:
            df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]

            mapping = {}
            for col in df.columns:
                # إزالة أي رموز خاصة
                new_col = re.sub(r'[^\w\s]', '', col)
                # استبدال المسافات بشرطة سفلية
                new_col = re.sub(r'\s+', '_', new_col.strip())
                mapping[col] = new_col

            df = df.rename(columns=mapping)
            return df

        except Exception as e:
            st.warning(f"⚠️ تحذير في تنظيف أسماء الأعمدة: {str(e)}")
            return df

    # -------------------------------------------------
    # إزالة الصفوف الفارغة
    # -------------------------------------------------
    def remove_empty_rows(self, df):
        """إزالة الصفوف الفارغة تماماً"""
        try:
            initial = len(df)
            df = df.dropna(how='all')
            removed = initial - len(df)
            if removed > 0:
                st.info(f"📊 تم إزالة {removed} صف فارغ")
            return df
        except Exception as e:
            st.warning(f"⚠️ تحذير في إزالة الصفوف الفارغة: {str(e)}")
            return df

    # -------------------------------------------------
    # تنظيف الأنواع
    # -------------------------------------------------
    def clean_data_types(self, df):
        """تحويل التواريخ والأعداد والنصوص لأشكال مناسبة"""
        try:
            # التواريخ
            date_cols = ['Date_Placed_in_Service', 'تاريخ_الدخول_في_الخدمة']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                    if df[col].isna().all():
                        # محاولة لاحقة بصيغة مختلفة
                        df[col] = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d %H:%M:%S')

            # الأعمدة الرقمية الشائعة باسمائها بعد التنظيف
            numeric_cols = [
                'Cost', 'التكلفة',
                'Depreciation_amount', 'قسط_الاهلاك',
                'Net_Book_Value', 'القيمة_الدفترية',
                'Useful_Life', 'العمر_الإنتاجي',
                'Quantity', 'العدد',
                'Residual_Value', 'القيمة_المتبقية_في_نهاية_العمر',
                'Accumulated_Depreciation', 'الاستهلاك_المتراكم'
            ]

            for col in numeric_cols:
                if col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = (
                            df[col].astype(str)
                                  .str.replace(',', '', regex=False)
                                  .str.replace(' ', '', regex=False)
                        )
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # نصوص
            text_cols = [
                'Asset_Description', 'وصف_الأصل',
                'Custodian', 'القسم_أو_الإدارة_المسؤولة',
                'City', 'المدينة',
                'Level_1_FA_Module_-_English_Description',
                'Manufacturer', 'المصنع',
                'Tag_number', 'رقم_البطاقة'
            ]
            for col in text_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace(['Not Available', 'N/A', 'nan', 'None'], '')

            return df

        except Exception as e:
            st.warning(f"⚠️ تحذير في تنظيف أنواع البيانات: {str(e)}")
            return df

    # -------------------------------------------------
    # معالجة القيم المفقودة
    # -------------------------------------------------
    def handle_missing_values(self, df):
        """ملء/عرض تقرير عن القيم المفقودة"""
        try:
            missing_report = {}
            for col in df.columns:
                n = df[col].isna().sum()
                if n > 0:
                    pct = (n / len(df)) * 100
                    missing_report[col] = {'count': n, 'percentage': round(pct, 2)}

                    if col in ['Cost', 'Depreciation_amount', 'Net_Book_Value']:
                        df[col] = df[col].fillna(0)
                    elif col in ['Asset_Description', 'Custodian']:
                        df[col] = df[col].fillna('غير محدد')

            if missing_report:
                st.warning("⚠️ يوجد قيم مفقودة في البيانات")
                # عرض الأعمدة ذات النسب الأعلى فقط للاختصار
                for col, info in missing_report.items():
                    if info['percentage'] > 5:
                        st.write(f"   - {col}: {info['count']} قيم مفقودة ({info['percentage']}%)")

            return df

        except Exception as e:
            st.warning(f"⚠️ تحذير في معالجة القيم المفقودة: {str(e)}")
            return df

    # -------------------------------------------------
    # الأعمدة المحسوبة (الإصدار المعتمد)
    # -------------------------------------------------
    @staticmethod
def calculate_additional_metrics(df):
        """إضافة أعمدة محسوبة مثل العمر ونسبة الإهلاك والتصنيفات"""
        try:
            # 1) حساب عمر الأصل (بالسنوات) بدون استخدام وحدة 'Y'
            #    نحول الفرق إلى أيام ثم نقسم على 365.25
            if 'Date_Placed_in_Service' in df.columns:
                now = pd.Timestamp.now()
                age_days = (now - pd.to_datetime(df['Date_Placed_in_Service'], errors='coerce')).dt.days
                df['Asset_Age'] = (age_days / 365.25).round(1)
            else:
                # إن لم تتوفر، اجعلها صفر لتجنب أخطاء لاحقة
                df['Asset_Age'] = 0.0

            # 2) نسبة الإهلاك
            if 'Cost' in df.columns and 'Depreciation_amount' in df.columns:
                df['Depreciation_Rate'] = (df['Depreciation_amount'] / df['Cost']) * 100
                df['Depreciation_Rate'] = df['Depreciation_Rate'].replace([np.inf, -np.inf], np.nan).fillna(0)
                df['Depreciation_Rate'] = df['Depreciation_Rate'].clip(0, 100).round(2)

            # 3) تصنيف حالة الأصل
            if 'Depreciation_Rate' in df.columns:
                conds = [
                    df['Depreciation_Rate'] >= 80,
                    df['Depreciation_Rate'] >= 50,
                    df['Depreciation_Rate'] >= 20,
                    df['Depreciation_Rate'] > 0
                ]
                labels = ['قديم', 'متوسط', 'جديد', 'جديد جداً']
                df['Asset_Condition'] = np.select(conds, labels, default='لم يبدأ الإهلاك')

            # 4) تصنيف قيمة الأصل
            if 'Cost' in df.columns:
                conds = [df['Cost'] >= 10000, df['Cost'] >= 5000, df['Cost'] >= 1000]
                labels = ['عالية', 'متوسطة', 'منخفضة']
                df['Value_Category'] = np.select(conds, labels, default='very_low')

            # 5) العمر المتبقي
            if 'Useful_Life' in df.columns:
                df['Remaining_Life'] = (df['Useful_Life'] - df['Asset_Age']).round(1)
                df['Remaining_Life'] = df['Remaining_Life'].clip(lower=0)

            # 6) سنة التشغيل
            if 'Date_Placed_in_Service' in df.columns:
                d = pd.to_datetime(df['Date_Placed_in_Service'], errors='coerce')
                df['Service_Year'] = d.dt.year

            st.info("📈 تم إضافة الأعمدة المحسوبة بنجاح")
            return df

        except Exception as e:
            st.warning(f"⚠️ تحذير في إضافة الأعمدة المحسوبة: {str(e)}")
            return df

    # -------------------------------------------------
    # توافق خلفي مع استدعاء app.py
    # -------------------------------------------------
    def add_calculated_columns(self, df):
        """توافق: اسم قديم يستدعي نفس الدالة الحالية"""
        return self.calculate_additional_metrics(df)

    # -------------------------------------------------
    # فحوص جودة البيانات
    # -------------------------------------------------
    def validate_data_quality(self, df):
        """التحقق من جودة البيانات"""
        try:
            issues = []

            if 'Cost' in df.columns:
                neg = df[df['Cost'] < 0]
                if len(neg) > 0:
                    issues.append(f"❌ تكاليف سلبية: {len(neg)} سجل")

            if 'Cost' in df.columns and 'Depreciation_amount' in df.columns:
                over = df[df['Depreciation_amount'] > df['Cost']]
                if len(over) > 0:
                    issues.append(f"❌ إهلاك زائد عن التكلفة: {len(over)} سجل")

            if 'Net_Book_Value' in df.columns:
                nbv_neg = df[df['Net_Book_Value'] < 0]
                if len(nbv_neg) > 0:
                    issues.append(f"❌ قيم دفترية سلبية: {len(nbv_neg)} سجل")

            if 'Asset_Age' in df.columns:
                age_neg = df[df['Asset_Age'] < 0]
                if len(age_neg) > 0:
                    issues.append(f"❌ أعمار سلبية: {len(age_neg)} سجل")

            if 'Tag_number' in df.columns:
                dup = df[df.duplicated('Tag_number', keep=False)]
                if len(dup) > 0:
                    issues.append(f"❌ أرقام بطاقات مكررة: {len(dup)} سجل")

            if issues:
                st.warning("⚠️ مشاكل في جودة البيانات:")
                for i in issues:
                    st.write(f"   {i}")
            else:
                st.success("✅ جودة البيانات ممتازة")

            return issues

        except Exception as e:
            st.warning(f"⚠️ تحذير في التحقق من جودة البيانات: {str(e)}")
            return []

    # -------------------------------------------------
    # ملخص/تصدير/تصفية
    # -------------------------------------------------
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

            if 'Date_Placed_in_Service' in df.columns:
                d = pd.to_datetime(df['Date_Placed_in_Service'], errors='coerce')
                summary['date_range'] = {'min': d.min(), 'max': d.max()}

            if 'Cost' in df.columns:
                summary['cost_range'] = {
                    'min': float(pd.to_numeric(df['Cost'], errors='coerce').min()),
                    'max': float(pd.to_numeric(df['Cost'], errors='coerce').max()),
                    'total': float(pd.to_numeric(df['Cost'], errors='coerce').sum())
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
            out = df.copy()
            for column, value in filters.items():
                if value and column in out.columns:
                    if isinstance(value, (int, float)):
                        out = out[out[column] == value]
                    else:
                        out = out[out[column].astype(str).str.contains(str(value), case=False, na=False)]
            return out
        except Exception as e:
            st.error(f"❌ خطأ في تصفية البيانات: {str(e)}")
            return df


# -----------------------------------------------------
# أدوات التحقق الإضافية
# -----------------------------------------------------
class DataValidator:
    @staticmethod
    def validate_asset_data(df):
        """التحقق من صحة بيانات الأصول"""
        results = {'passed': [], 'warnings': [], 'errors': []}
        try:
            required = ['Cost', 'Asset_Description', 'Tag_number']
            for col in required:
                if col not in df.columns:
                    results['errors'].append(f"العمود المطلوب '{col}' غير موجود")

            if 'Tag_number' in df.columns:
                dup = df[df.duplicated('Tag_number', keep=False)]
                if len(dup) > 0:
                    results['warnings'].append(f"يوجد {len(dup)} رقم بطاقة مكرر")

            for col in ['Cost', 'Depreciation_amount', 'Net_Book_Value']:
                if col in df.columns:
                    if df[col].isna().any():
                        results['warnings'].append(f"يوجد قيم مفقودة في {col}")
                    if (df[col] < 0).any():
                        results['warnings'].append(f"يوجد قيم سلبية في {col}")

            if not results['errors']:
                results['passed'].append("جميع الاختبارات الأساسية نجحت")
            return results

        except Exception as e:
            results['errors'].append(f"خطأ في التحقق من البيانات: {str(e)}")
            return results


# -----------------------------------------------------
# تقارير وأنماط
# -----------------------------------------------------
def detect_data_patterns(df):
    """كشف أنماط البيانات (سنوي/مدن/تصنيفات)"""
    patterns = {}
    try:
        if 'Service_Year' in df.columns:
            patterns['yearly_distribution'] = df['Service_Year'].value_counts().sort_index().to_dict()
        if 'City' in df.columns:
            patterns['city_distribution'] = df['City'].value_counts().to_dict()
        if 'Level_1_FA_Module_-_English_Description' in df.columns:
            patterns['category_distribution'] = df['Level_1_FA_Module_-_English_Description'].value_counts().to_dict()
        return patterns
    except Exception as e:
        st.warning(f"⚠️ تحذير في كشف الأنماط: {str(e)}")
        return {}

def generate_data_report(df):
    """إنشاء تقرير شامل عن البيانات"""
    return {
        'basic_info': {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'memory_usage': float(df.memory_usage(deep=True).sum()) / (1024 ** 2)  # MB
        },
        'data_quality': {},
        'patterns': detect_data_patterns(df)
    }
