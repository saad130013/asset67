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
        """تحميل البيانات من Excel"""
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        if df.empty:
            raise ValueError("الملف لا يحتوي على بيانات")
        st.success(f"✅ تم تحميل {len(df)} سجل بنجاح")
        return df

    # --------- مراحل المعالجة ---------
    def preprocess_data(self, df):
        """تنظيف أولي + أنواع + مفقودات"""
        self.raw_df = df.copy()
        df = self.clean_column_names(df)
        df = self.remove_empty_rows(df)
        df = self.clean_data_types(df)
        df = self.handle_missing_values(df)
        self.processed_df = df
        st.success("✅ تم معالجة البيانات بنجاح")
        return df

    def clean_column_names(self, df):
        """تنظيف أسماء الأعمدة (مع الاحتفاظ بإمكانية إنشاء aliases لاحقاً)"""
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
        mapping = {}
        for col in df.columns:
            clean = re.sub(r'[^\w\s]', '', col)
            clean = re.sub(r'\s+', '_', clean.strip())
            mapping[col] = clean
        df = df.rename(columns=mapping)
        return df

    def remove_empty_rows(self, df):
        initial = len(df)
        df = df.dropna(how='all')
        removed = initial - len(df)
        if removed > 0:
            st.info(f"📊 تم إزالة {removed} صف فارغ")
        return df

    def clean_data_types(self, df):
        # تواريخ
        for col in ['Date_Placed_in_Service', 'تاريخ_الدخول_في_الخدمة']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                if df[col].isna().all():
                    df[col] = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d %H:%M:%S')
        # أرقام
        numeric_cols = [
            'Cost','التكلفة','Depreciation_amount','قسط_الاهلاك','Net_Book_Value','القيمة_الدفترية',
            'Useful_Life','العمر_الإنتاجي','Quantity','العدد','Residual_Value','القيمة_المتبقية_في_نهاية_العمر',
            'Accumulated_Depreciation','الاستهلاك_المتراكم'
        ]
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        # نصوص
        text_cols = [
            'Asset_Description','وصف_الأصل','Custodian','القسم_أو_الإدارة_المسؤولة',
            'City','المدينة','Level_1_FA_Module_English_Description',
            'Manufacturer','المصنع','Tag_number','رقم_البطاقة'
        ]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace(['Not Available','N/A','nan','None'], '')
        return df

    def handle_missing_values(self, df):
        for col in df.columns:
            if df[col].isna().sum() == 0:
                continue
            if col in ['Cost', 'Depreciation_amount', 'Net_Book_Value']:
                df[col] = df[col].fillna(0)
            elif col in ['Asset_Description', 'Custodian']:
                df[col] = df[col].fillna('غير محدد')
        return df

    # حسابات مضافة + إرجاع أعمدة بالأسماء القياسية (المتوافقة مع asset_models)
    @staticmethod
    def calculate_additional_metrics(df):
        # عمر الأصل
        if 'Date_Placed_in_Service' in df.columns:
            now = pd.Timestamp.now()
            df['Asset_Age'] = (now - pd.to_datetime(df['Date_Placed_in_Service'])) / np.timedelta64(1, 'Y')
            df['Asset_Age'] = df['Asset_Age'].round(1)
        # نسبة الإهلاك
        if 'Cost' in df.columns and 'Depreciation_amount' in df.columns:
            df['Depreciation_Rate'] = (df['Depreciation_amount'] / df['Cost'] * 100).replace([np.inf, -np.inf], 0).clip(0, 100).round(2)
        # حالة الأصل
        if 'Depreciation_Rate' in df.columns:
            conds = [df['Depreciation_Rate'] >= 80, df['Depreciation_Rate'] >= 50, df['Depreciation_Rate'] >= 20, df['Depreciation_Rate'] > 0]
            choices = ['قديم','متوسط','جديد','جديد جداً']
            df['Asset_Condition'] = np.select(conds, choices, default='لم يبدأ الإهلاك')
        return df

    def standardize_column_aliases(self, df):
        """إنشاء أعمدة aliases بأسماء المسافات التي يتوقعها asset_models"""
        aliases = {
            'Date_Placed_in_Service': 'Date Placed in Service',
            'Depreciation_amount': 'Depreciation amount',
            'Net_Book_Value': 'Net Book Value',
            'Useful_Life': 'Useful Life',
            'Asset_Description': 'Asset Description',
            'Tag_number': 'Tag number'
        }
        for src, dst in aliases.items():
            if src in df.columns and dst not in df.columns:
                df[dst] = df[src]
        return df
