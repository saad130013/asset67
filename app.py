import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        font-size: 1.5rem;
        color: #2e86ab;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class FixedAssetsApp:
    def __init__(self):
        self.df = None
        self.analyzer = None
        self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        try:
            self.df = data_processor.DataProcessor.load_data(
                config.APP_CONFIG["DATA_FILE"], 
                config.APP_CONFIG["SHEET_NAME"]
            )
            self.df = data_processor.DataProcessor.preprocess_data(self.df)
            self.df = data_processor.DataProcessor.calculate_additional_metrics(self.df)
            self.analyzer = asset_models.AssetAnalyzer(self.df)
            st.success("✅ تم تحميل البيانات بنجاح")
        except Exception as e:
            st.error(f"❌ خطأ في تحميل البيانات: {str(e)}")
    
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        st.markdown('<div class="main-header">🏢 نظام إدارة الأصول الثابتة</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">هيئة المساحة الجيولوجية السعودية - {config.APP_CONFIG["ENTITY_CODE"]}</div>', unsafe_allow_html=True)
        
        # الإحصائيات الرئيسية
        if self.analyzer:
            stats = self.analyzer.get_summary_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي الأصول", f"{stats['total_assets']:,}")
            
            with col2:
                st.metric("التكلفة الإجمالية", f"﷼{stats['total_cost']:,.0f}")
            
            with col3:
                st.metric("إجمالي الإهلاك", f"﷼{stats['total_depreciation']:,.0f}")
            
            with col4:
                st.metric("القيمة الدفترية", f"﷼{stats['total_net_value']:,.0f}")
    
    def show_category_analysis(self):
        """تحليل التصنيفات"""
        st.markdown('<div class="sub-header">📊 تحليل الأصول حسب التصنيف</div>', unsafe_allow_html=True)
        
        if self.analyzer:
            category_data = self.analyzer.get_assets_by_category()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # رسم بياني دائري
                fig_pie = px.pie(
                    values=category_data['Cost'],
                    names=category_data.index,
                    title="توزيع التكلفة حسب التصنيف"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # رسم بياني شريطي
                fig_bar = px.bar(
                    category_data,
                    y=category_data.index,
                    x='Cost',
                    title="التكلفة حسب التصنيف",
                    orientation='h'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
    
    def show_location_analysis(self):
        """تحليل المواقع"""
        st.markdown('<div class="sub-header">📍 تحليل الأصول حسب الموقع</div>', unsafe_allow_html=True)
        
        if self.analyzer:
            location_data = self.analyzer.get_assets_by_location()
            
            fig = px.bar(
                location_data,
                x=location_data.index,
                y=['Cost', 'Net Book Value'],
                title="التكلفة والقيمة الدفترية حسب الموقع",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_depreciation_analysis(self):
        """تحليل الإهلاك"""
        st.markdown('<div class="sub-header">📉 تحليل الإهلاك</div>', unsafe_allow_html=True)
        
        if self.analyzer:
            dep_data = self.analyzer.get_depreciation_analysis()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # توزيع حالة الأصول
                condition_counts = self.df['Asset_Condition'].value_counts()
                fig_condition = px.pie(
                    values=condition_counts.values,
                    names=condition_counts.index,
                    title="توزيع حالة الأصول"
                )
                st.plotly_chart(fig_condition, use_container_width=True)
            
            with col2:
                # علاقة العمر بالإهلاك
                fig_scatter = px.scatter(
                    self.df,
                    x='Asset_Age',
                    y='Depreciation_Percentage',
                    color='Asset_Condition',
                    title="علاقة عمر الأصل بنسبة الإهلاك",
                    size='Cost',
                    hover_data=['Asset Description']
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    def show_search_functionality(self):
        """وظيفة البحث"""
        st.markdown('<div class="sub-header">🔍 بحث في الأصول</div>', unsafe_allow_html=True)
        
        search_term = st.text_input("أدخل كلمة للبحث (وصف الأصل، القسم، الموقع، رقم البطاقة):")
        
        if search_term and self.analyzer:
            results = self.analyzer.search_assets(search_term)
            st.write(f"تم العثور على {len(results)} أصل")
            st.dataframe(results[['Asset Description', 'Custodian', 'City', 'Cost', 'Net Book Value']])
    
    def show_raw_data(self):
        """عرض البيانات الخام"""
        st.markdown('<div class="sub-header">📋 البيانات الخام</div>', unsafe_allow_html=True)
        
        if self.df is not None:
            st.dataframe(self.df, use_container_width=True)
    
    def run(self):
        """تشغيل التطبيق"""
        # الشريط الجانبي
        st.sidebar.title("خيارات التطبيق")
        app_section = st.sidebar.selectbox(
            "اختر قسم التطبيق:",
            ["لوحة التحكم", "تحليل التصنيفات", "تحليل المواقع", "تحليل الإهلاك", "بحث في الأصول", "البيانات الخام"]
        )
        
        # عرض الأقسام
        if app_section == "لوحة التحكم":
            self.show_dashboard()
        elif app_section == "تحليل التصنيفات":
            self.show_category_analysis()
        elif app_section == "تحليل المواقع":
            self.show_location_analysis()
        elif app_section == "تحليل الإهلاك":
            self.show_depreciation_analysis()
        elif app_section == "بحث في الأصول":
            self.show_search_functionality()
        elif app_section == "البيانات الخام":
            self.show_raw_data()
        
        # معلومات إضافية في الشريط الجانبي
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **معلومات عن النظام:**
        - إصدار 1.0
        - تاريخ التحديث: 2024
        - للاستخدام الداخلي
        """)

# تشغيل التطبيق
if __name__ == "__main__":
    app = FixedAssetsApp()
    app.run()
