# -*- coding: utf-8 -*-
"""
إعدادات التطبيق - نظام إدارة الأصول الثابتة
هيئة المساحة الجيولوجية السعودية
"""

# =============================================================================
# إعدادات التطبيق الأساسية
# =============================================================================

APP_CONFIG = {
    "APP_NAME": "نظام إدارة الأصول الثابتة",
    "VERSION": "1.0.0",
    "DESCRIPTION": "نظام ذكي لإدارة وتحليل الأصول الثابتة بهيئة المساحة الجيولوجية السعودية",
    "AUTHOR": "هيئة المساحة الجيولوجية السعودية",
    "RELEASE_DATE": "2024",
    
    # إعدادات البيانات
    "DATA_FILE": "assetv1.xlsx",
    "SHEET_NAME": "FAR as of 30 Dec 23",
    "BACKUP_DATA": True,
    "AUTO_SAVE": True,
    
    # إعدادات الواجهة
    "LANGUAGE": "ar",
    "THEME": "light",
    "DIRECTION": "rtl",
    
    # إعدادات الأمان
    "ENCRYPT_DATA": False,
    "LOG_ACTIVITY": True
}

# =============================================================================
# إعدادات الكيان
# =============================================================================

ENTITY_CONFIG = {
    "NAME_ARABIC": "هيئة المساحة الجيولوجية السعودية",
    "NAME_ENGLISH": "Saudi Geological Survey",
    "ENTITY_CODE": "0047",
    "LOCATION": "جدة, المملكة العربية السعودية",
    "CURRENCY": "SAR",
    "CURRENCY_SYMBOL": "﷼",
    "FISCAL_YEAR_START": "01-01",
    "FISCAL_YEAR_END": "12-31"
}

# =============================================================================
# أسماء الأعمدة في البيانات
# =============================================================================

COLUMN_MAPPING = {
    # المعلومات الأساسية
    'entity': 'Entity',
    'entity_code': 'Entity Code',
    'entity_arabic': 'اسم الجهة',
    
    # التصنيف الهرمي
    'level1_code': 'Level 1 FA Module Code',
    'level1_arabic': 'Level 1 FA Module - Arabic Description',
    'level1_english': 'Level 1 FA Module - English Description',
    
    'level2_code': 'Level 2 FA Module Code',
    'level2_arabic': 'Level 2 FA Module - Arabic Description',
    'level2_english': 'Level 2 FA Module - English Description',
    
    'level3_code': 'Level 3 FA Module Code',
    'level3_arabic': 'Level 3 FA Module - Arabic Description',
    'level3_english': 'Level 3 FA Module - English Description',
    
    # المجموعة المحاسبية
    'accounting_group_code': 'accounting group Code',
    'accounting_group_arabic': 'accounting group Arabic Description',
    'accounting_group_english': 'accounting group English Description',
    
    # معلومات الأصل
    'asset_code': 'Asset Code For Accounting Purpose',
    'asset_description_ar': 'Asset Description For Maintenance Purpose',
    'asset_description_en': 'Asset Description',
    'asset_functional_code': 'Asset Functional Code',
    
    # المعلومات المالية
    'cost': 'Cost',
    'depreciation_amount': 'Depreciation amount',
    'accumulated_depreciation': 'Accumulated Depreciation',
    'residual_value': 'Residual Value',
    'net_book_value': 'Net Book Value',
    'useful_life': 'Useful Life',
    'remaining_life': 'Remaining useful life',
    
    # المعلومات الإدارية
    'gl_account': 'GL account',
    'cost_center': 'Cost Center',
    'asset_owner': 'Asset Owner',
    'custodian': 'Custodian',
    'consolidated_code': 'Consolidated Code',
    
    # المعلومات الفنية
    'tag_number': 'Tag number',
    'base_unit': 'Base Unit of Measure',
    'quantity': 'Quantity',
    'manufacturer': 'Manufacturer',
    'date_in_service': 'Date Placed in Service',
    
    # المعلومات الجغرافية
    'country': 'Country',
    'region': 'Region',
    'city': 'City',
    'coordinates': 'Geographical Coordinates',
    'national_address': 'National Address ID',
    'building_number': 'Building Number',
    'floors_number': 'Floors Number',
    'room_number': 'Room/office Number',
    
    # الأرقام الفريدة
    'mof_unique_number': 'Unique Asset Number in MoF system',
    'entity_unique_number': 'Unique Asset Number in the entity',
    'linked_asset': 'Linked/Associated Asset'
}

# =============================================================================
# التصنيفات والمجموعات
# =============================================================================

ASSET_CATEGORIES = {
    '13': {
        'code': '13',
        'name_ar': 'أصول تقنية المعلومات',
        'name_en': 'Information Technology Assets',
        'subcategories': {
            '01': {'name_ar': 'معدات الشبكة', 'name_en': 'Network Equipment'},
            '02': {'name_ar': 'تكنولوجيا المعلومات ومعدات الاتصالات المكتبية', 'name_en': 'Office IT and Communication Equipment'},
        }
    },
    '19': {
        'code': '19',
        'name_ar': 'معدات المختبرات والأجهزة',
        'name_en': 'Laboratory and instrumentation equipment',
        'subcategories': {
            '12': {'name_ar': 'أدوات القياس والمراقبة والاختبار', 'name_en': 'Measuring and Observing and Testing Instruments'},
        }
    },
    '20': {
        'code': '20',
        'name_ar': 'الآلات والمعدات الأخرى',
        'name_en': 'Other Machinery and Equipment',
        'subcategories': {
            '13': {'name_ar': 'معدات منزلية', 'name_en': 'Household Equipment'},
        }
    }
}

# =============================================================================
# إعدادات التحليل والتقارير
# =============================================================================

ANALYSIS_CONFIG = {
    # حدود التحليل
    'HIGH_VALUE_THRESHOLD': 10000,
    'MEDIUM_VALUE_THRESHOLD': 5000,
    'LOW_VALUE_THRESHOLD': 1000,
    
    # تصنيف الإهلاك
    'DEPRECIATION_LEVELS': {
        'NEW': 20,
        'GOOD': 50,
        'AVERAGE': 80,
        'OLD': 100
    },
    
    # فترات التقارير
    'REPORT_PERIODS': ['شهري', 'ربع سنوي', 'نصف سنوي', 'سنوي'],
    
    # أنواع التقارير
    'REPORT_TYPES': {
        'summary': 'تقرير ملخص',
        'depreciation': 'تقرير الإهلاك',
        'categorical': 'تقرير تصنيفي',
        'location': 'تقرير جغرافي',
        'custodian': 'تقرير بالأقسام'
    }
}

# =============================================================================
# إعدادات الواجهة والعرض
# =============================================================================

UI_CONFIG = {
    # الألوان
    'COLORS': {
        'primary': '#1f77b4',
        'secondary': '#2e86ab',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    },
    
    # الثيمات
    'THEMES': {
        'light': {
            'background': '#ffffff',
            'primary': '#1f77b4',
            'text': '#333333'
        },
        'dark': {
            'background': '#1e1e1e',
            'primary': '#4a90e2',
            'text': '#ffffff'
        }
    },
    
    # الأحجام
    'SIZES': {
        'sidebar_width': 300,
        'chart_height': 400,
        'table_height': 600
    },
    
    # الخطوط
    'FONTS': {
        'primary': 'Arial, sans-serif',
        'arabic': '"Arabic Typesetting", "Traditional Arabic", "Arial", sans-serif'
    }
}

# =============================================================================
# إعدادات الرسوم البيانية
# =============================================================================

CHART_CONFIG = {
    'COLOR_SCHEME': 'plotly',
    'TEMPLATE': 'plotly_white',
    'DEFAULT_WIDTH': 800,
    'DEFAULT_HEIGHT': 500,
    
    'CHART_TYPES': {
        'bar': 'رسم بياني شريطي',
        'line': 'رسم بياني خطي',
        'pie': 'رسم بياني دائري',
        'scatter': 'رسم بياني مبعثر',
        'histogram': 'رسم توزيع'
    },
    
    'ANIMATION_SETTINGS': {
        'enabled': True,
        'duration': 1000
    }
}

# =============================================================================
# إعدادات البحث والتصفية
# =============================================================================

SEARCH_CONFIG = {
    'MIN_SEARCH_LENGTH': 2,
    'MAX_RESULTS': 100,
    'SEARCH_FIELDS': [
        'Asset Description',
        'Custodian',
        'City',
        'Tag number',
        'Level 1 FA Module - English Description',
        'Manufacturer',
        'Asset Code For Accounting Purpose'
    ],
    
    'FILTER_OPTIONS': {
        'location': ['جدة', 'الرياض', 'مكة المكرمة'],
        'category': ['Information Technology Assets', 'Laboratory and instrumentation equipment', 'Other Machinery and Equipment'],
        'condition': ['جديد جداً', 'جديد', 'متوسط', 'قديم'],
        'value_category': ['عالية', 'متوسطة', 'منخفضة']
    }
}

# =============================================================================
# إعدادات التصدير والاستيراد
# =============================================================================

EXPORT_CONFIG = {
    'SUPPORTED_FORMATS': ['xlsx', 'csv', 'pdf'],
    'DEFAULT_FORMAT': 'xlsx',
    'INCLUDE_CHARTS': True,
    'COMPRESS_FILES': True,
    
    'EXPORT_OPTIONS': {
        'full_data': 'جميع البيانات',
        'filtered_data': 'البيانات المصفاة',
        'summary_report': 'تقرير ملخص',
        'analysis_report': 'تقرير تحليلي'
    }
}

# =============================================================================
# رسائل النظام
# =============================================================================

MESSAGES = {
    'ar': {
        'welcome': 'مرحباً بك في نظام إدارة الأصول الثابتة',
        'loading_data': 'جاري تحميل البيانات...',
        'processing_data': 'جاري معالجة البيانات...',
        'data_loaded_success': 'تم تحميل البيانات بنجاح',
        'data_processed_success': 'تم معالجة البيانات بنجاح',
        'search_no_results': 'لم يتم العثور على نتائج',
        'export_success': 'تم التصدير بنجاح',
        'error_loading_file': 'خطأ في تحميل الملف',
        'error_processing_data': 'خطأ في معالجة البيانات'
    },
    'en': {
        'welcome': 'Welcome to Fixed Assets Management System',
        'loading_data': 'Loading data...',
        'processing_data': 'Processing data...',
        'data_loaded_success': 'Data loaded successfully',
        'data_processed_success': 'Data processed successfully',
        'search_no_results': 'No results found',
        'export_success': 'Export completed successfully',
        'error_loading_file': 'Error loading file',
        'error_processing_data': 'Error processing data'
    }
}

# =============================================================================
# الثوابت الحسابية
# =============================================================================

CALCULATION_CONSTANTS = {
    'DAYS_IN_YEAR': 365,
    'MONTHS_IN_YEAR': 12,
    'DEPRECIATION_METHOD': 'straight_line',  # القسط الثابت
    'SALVAGE_VALUE_RATE': 0.05,  # 5% قيمة متبقية
    'MAX_USEFUL_LIFE': 50,  # أقصى عمر إنتاجي
    'MIN_USEFUL_LIFE': 1    # أدنى عمر إنتاجي
}

# =============================================================================
# إعدادات النسخ الاحتياطي
# =============================================================================

BACKUP_CONFIG = {
    'ENABLED': True,
    'AUTO_BACKUP': True,
    'BACKUP_INTERVAL': 24,  # ساعات
    'MAX_BACKUP_FILES': 10,
    'BACKUP_PATH': 'backups/'
}

# =============================================================================
# دوال مساعدة للوصول للإعدادات
# =============================================================================

def get_column_name(key, language='ar'):
    """الحصول على اسم العمود باللغة المطلوبة"""
    column_key = COLUMN_MAPPING.get(key)
    if not column_key:
        return key
    
    # في التطبيق الفعلي، يمكن إضافة ترجمة ديناميكية هنا
    return column_key

def get_category_name(category_code, language='ar'):
    """الحصول على اسم التصنيف"""
    category = ASSET_CATEGORIES.get(category_code, {})
    if language == 'ar':
        return category.get('name_ar', category_code)
    else:
        return category.get('name_en', category_code)

def get_message(message_key, language='ar'):
    """الحصول على رسالة النظام"""
    return MESSAGES.get(language, {}).get(message_key, message_key)

def get_analysis_threshold(threshold_type):
    """الحصول على حدود التحليل"""
    return ANALYSIS_CONFIG.get(threshold_type, 0)

# =============================================================================
# معلومات الإصدار والتحديث
# =============================================================================

VERSION_INFO = {
    'current_version': '1.0.0',
    'release_date': '2024-01-01',
    'changelog': [
        '1.0.0: الإصدار الأول - نظام إدارة الأصول الثابتة',
        'المميزات: تحميل البيانات، التحليل، التقارير، البحث'
    ],
    'update_url': '',
    'support_contact': 'دعم التقنية - هيئة المساحة الجيولوجية السعودية'
}

# =============================================================================
# التحقق من صحة الإعدادات
# =============================================================================

def validate_config():
    """التحقق من صحة الإعدادات"""
    errors = []
    
    # التحقق من وجود ملف البيانات
    import os
    if not os.path.exists(APP_CONFIG['DATA_FILE']):
        errors.append(f"ملف البيانات {APP_CONFIG['DATA_FILE']} غير موجود")
    
    # التحقق من التصنيفات
    required_categories = ['13', '19', '20']
    for cat in required_categories:
        if cat not in ASSET_CATEGORIES:
            errors.append(f"التصنيف {cat} غير موجود في الإعدادات")
    
    return errors

# التحقق من الإعدادات عند التحميل
config_errors = validate_config()
if config_errors:
    print("تحذير: هناك أخطاء في الإعدادات:")
    for error in config_errors:
        print(f" - {error}")