import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

import asset_models
import data_processor
import config

# إعداد الصفحة
st.set_page_config(
    page_title="نظام إدارة الأصول الثابتة",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# التصميم العربي
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #2e86ab;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class FixedAssetsApp:
    def __init__(self):
        self.df = None
        self.analyzer = None
        self.load_data()

def load_data(self):
    try:
        # تحميل البيانات من ملف Excel
        self.df = data_processor.DataProcessor.load_data(
            config.APP_CONFIG["DATA_FILE"],
            config.APP_CONFIG["SHEET_NAME"]
        )

        # تنفيذ المعالجة المسبقة
        self.df = data_processor.DataProcessor.preprocess_data(self.df)

        # إضافة الأعمدة المحسوبة (مثل العمر ونسبة الإهلاك)
        self.df = data_processor.DataProcessor.calculate_additional_metrics(self.df)

        # إنشاء محلل البيانات
        self.analyzer = asset_models.AssetAnalyzer(self.df)

        # رسالة نجاح
        st.success("✅ تم تحميل البيانات بنجاح")

    except Exception as e:
        st.error(f"❌ خطأ في تحميل/معالجة البيانات: {str(e)}")
        """تحميل البيانات ومعالجتها"""
        try:
            # 1) تحميل
            df = data_processor.DataProcessor.load_data(
                config.APP_CONFIG["DATA_FILE"],
                config.APP_CONFIG["SHEET_NAME"]
            )
            # 2) معالجة مسبقة + إضافات حسابية + إعادة الأسماء القياسية
            dp = data_processor.DataProcessor()
            df = dp.preprocess_data(df)
            df = data_processor.DataProcessor.calculate_additional_metrics(df)
            df = dp.standardize_column_aliases(df)

            # 3) محلل البيانات
            self.df = df
            self.analyzer = asset_models.AssetAnalyzer(self.df)
            st.success("✅ تم تحميل البيانات ومعالجتها بنجاح")
        except Exception as e:
            st.error(f"❌ خطأ في تحميل/معالجة البيانات: {str(e)}")

    def show_dashboard(self):
        st.markdown('<div class="main-header">🏢 نظام إدارة الأصول الثابتة</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sub-header">هيئة المساحة الجيولوجية السعودية - {config.ENTITY_CONFIG.get("ENTITY_CODE","")}</div>',
            unsafe_allow_html=True
        )

        if self.analyzer:
            stats = self.analyzer.get_summary_stats()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("إجمالي الأصول", f"{stats.get('total_assets',0):,}")
            c2.metric("التكلفة الإجمالية", f"﷼{stats.get('total_cost',0):,.0f}")
            c3.metric("إجمالي الإهلاك", f"﷼{stats.get('total_depreciation',0):,.0f}")
            c4.metric("القيمة الدفترية", f"﷼{stats.get('total_net_value',0):,.0f}")

    def show_category_analysis(self):
        st.markdown('<div class="sub-header">📊 تحليل الأصول حسب التصنيف</div>', unsafe_allow_html=True)
        if not self.analyzer:
            return
        category_data = self.analyzer.get_assets_by_category()
        if category_data.empty:
            st.info("لا توجد بيانات تصنيفية متاحة.")
            return
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(
                values=category_data['Cost'],
                names=category_data.index,
                title="توزيع التكلفة حسب التصنيف"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_bar = px.bar(
                category_data,
                y=category_data.index,
                x='Cost',
                title="التكلفة حسب التصنيف",
                orientation='h'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    def show_location_analysis(self):
        st.markdown('<div class="sub-header">📍 تحليل الأصول حسب الموقع</div>', unsafe_allow_html=True)
        if not self.analyzer:
            return
        location_data = self.analyzer.get_assets_by_location()
        if location_data.empty:
            st.info("لا توجد بيانات مواقع.")
            return
        fig = px.bar(
            location_data,
            x=location_data.index,
            y=['Cost', 'Net Book Value'],
            title="التكلفة والقيمة الدفترية حسب الموقع",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

    def show_depreciation_analysis(self):
        st.markdown('<div class="sub-header">📉 تحليل الإهلاك</div>', unsafe_allow_html=True)
        if not self.analyzer:
            return

        _ = self.analyzer.get_depreciation_analysis()  # يضيف أعمدة للحالة
        col1, col2 = st.columns(2)
        with col1:
            if 'Asset_Condition' in self.df.columns:
                counts = self.df['Asset_Condition'].value_counts()
                fig = px.pie(values=counts.values, names=counts.index, title="توزيع حالة الأصول")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد أعمدة حالة للأصول.")

        with col2:
            needed = {'Asset_Age', 'Depreciation_Rate', 'Cost', 'Asset Description'}
            if needed.issubset(self.df.columns):
                fig = px.scatter(
                    self.df,
                    x='Asset_Age',
                    y='Depreciation_Rate',
                    color='Asset_Condition',
                    title="علاقة عمر الأصل بنسبة الإهلاك",
                    size='Cost',
                    hover_data=['Asset Description']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد أعمدة كافية للرسم المبعثر.")

    def show_search_functionality(self):
        st.markdown('<div class="sub-header">🔍 بحث في الأصول</div>', unsafe_allow_html=True)
        term = st.text_input("أدخل كلمة للبحث (وصف الأصل، القسم، الموقع، رقم البطاقة):")
        if term and self.analyzer:
            results = self.analyzer.search_assets(term)
            st.write(f"تم العثور على {len(results)} أصل")
            cols = [c for c in ['Asset Description', 'Custodian', 'City', 'Cost', 'Net Book Value'] if c in results.columns]
            st.dataframe(results[cols] if cols else results)

    def show_raw_data(self):
        st.markdown('<div class="sub-header">📋 البيانات الخام</div>', unsafe_allow_html=True)
        if self.df is not None:
            st.dataframe(self.df, use_container_width=True)

    def run(self):
        st.sidebar.title("خيارات التطبيق")
        section = st.sidebar.selectbox(
            "اختر قسم التطبيق:",
            ["لوحة التحكم", "تحليل التصنيفات", "تحليل المواقع", "تحليل الإهلاك", "بحث في الأصول", "البيانات الخام"]
        )
        if section == "لوحة التحكم":
            self.show_dashboard()
        elif section == "تحليل التصنيفات":
            self.show_category_analysis()
        elif section == "تحليل المواقع":
            self.show_location_analysis()
        elif section == "تحليل الإهلاك":
            self.show_depreciation_analysis()
        elif section == "بحث في الأصول":
            self.show_search_functionality()
        else:
            self.show_raw_data()

        st.sidebar.markdown("---")
        st.sidebar.info("**إصدار** 1.0 — تحديث 2024 — للاستخدام الداخلي")

if __name__ == "__main__":
    app = FixedAssetsApp()
    app.run()
