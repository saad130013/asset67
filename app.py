import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(
    page_title="نظام إدارة الأصول الثابتة",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 نظام إدارة الأصول الثابتة")
st.success("التطبيق يعمل! تم إصلاح مشكلة المسافات.")

# اختبار الاستيراد
try:
    import data_processor
    st.info("✅ تم استيراد data_processor بنجاح")
except ImportError as e:
    st.error(f"❌ خطأ في استيراد data_processor: {e}")

try:
    import asset_models
    st.info("✅ تم استيراد asset_models بنجاح")
except ImportError as e:
    st.error(f"❌ خطأ في استيراد asset_models: {e}")

try:
    import config
    st.info("✅ تم استيراد config بنجاح")
except ImportError as e:
    st.error(f"❌ خطأ في استيراد config: {e}")
