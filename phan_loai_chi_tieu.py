import pandas as pd
import re


def classify_category(description: str) -> str:
    """
    Phân loại danh mục dựa trên mô tả giao dịch bằng keyword matching.
    
    Args:
        description (str): Mô tả giao dịch.
        
    Returns:
        str: Danh mục phân loại.
    """
    try:
        if not isinstance(description, str):
            return "Other"
        
        description_lower = description.lower()
        
        # Định nghĩa các từ khóa cho từng danh mục
        categories = {
            'Shopping': ['amazon', 'shopping', 'store', 'mall'],
            'Dining': ['restaurant', 'tavern', 'pub', 'cafe', 'food'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'cinema', 'game'],
            'Groceries': ['grocery', 'market', 'supermarket'],
            'Gas & Fuel': ['gas', 'fuel', 'shell', 'petrol'],
            'Utilities': ['phone', 'electric', 'water', 'internet'],
            'Income': ['salary', 'paycheck', 'bonus'],
            'Other': []  # Mặc định nếu không khớp
        }

        for category, keywords in categories.items():
            if category != 'Other' and keywords:
                if any(re.search(r'\b' + re.escape(keyword) + r'\b', description_lower) 
                       for keyword in keywords):
                    return category

        return 'Other'
        
    except Exception as exc:
        print(f"❌ Lỗi phân loại danh mục: {exc}")
        return 'Other'


def apply_auto_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Áp dụng phân loại tự động cho toàn bộ dataset.
    
    Args:
        df (pd.DataFrame): DataFrame chứa cột 'description'.
        
    Returns:
        pd.DataFrame: DataFrame với cột 'auto_category' được thêm.
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng")
            return df

        if 'description' not in df.columns:
            raise ValueError("DataFrame phải có cột 'description'")

        df = df.copy()
        df['auto_category'] = df['description'].apply(classify_category)

        return df
        
    except Exception as exc:
        print(f"❌ Lỗi áp dụng phân loại tự động: {exc}")
        return df