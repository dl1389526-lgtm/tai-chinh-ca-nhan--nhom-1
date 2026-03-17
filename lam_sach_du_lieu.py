import pandas as pd
import numpy as np


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa tên cột thành snake_case.
    
    Args:
        df (pd.DataFrame): DataFrame chứa các cột cần chuẩn hóa.
        
    Returns:
        pd.DataFrame: DataFrame với cột đã được chuẩn hóa.
    """
    try:
        df = df.rename(columns=lambda col: col.strip().lower().replace(' ', '_'))
        return df
    except Exception as exc:
        print(f"❌ Lỗi chuẩn hóa cột: {exc}")
        return df


def normalize_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa số tiền: debit = âm, credit = dương.
    
    Args:
        df (pd.DataFrame): DataFrame chứa cột 'transaction_type' và 'amount'.
        
    Returns:
        pd.DataFrame: DataFrame với số tiền đã được chuẩn hóa.
    """
    try:
        df = df.copy()

        if 'transaction_type' not in df.columns or 'amount' not in df.columns:
            raise ValueError("DataFrame phải có cột 'transaction_type' và 'amount'")

        df['transaction_type'] = df['transaction_type'].str.strip().str.lower()

        df['amount'] = np.where(
            df['transaction_type'] == 'debit',
            -abs(df['amount']),
            abs(df['amount'])
        )

        return df
    except Exception as exc:
        print(f"❌ Lỗi chuẩn hóa số tiền: {exc}")
        return df


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thêm cột year và month từ cột date.
    
    Args:
        df (pd.DataFrame): DataFrame chứa cột 'date'.
        
    Returns:
        pd.DataFrame: DataFrame với cột year và month được thêm.
    """
    try:
        df = df.copy()

        if 'date' not in df.columns:
            raise ValueError("DataFrame phải có cột 'date'")

        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month

        return df
    except Exception as exc:
        print(f"❌ Lỗi thêm date features: {exc}")
        return df


def remove_outliers_iqr(df: pd.DataFrame, column: str = 'amount', iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """
    Xóa outliers bằng phương pháp IQR (Interquartile Range).
    
    Công thức:
    - Q1 = Phần tư thứ 1 (25%)
    - Q3 = Phần tư thứ 3 (75%)
    - IQR = Q3 - Q1
    - Outlier nếu x > Q3 + 1.5*IQR hoặc x < Q1 - 1.5*IQR
    
    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu.
        column (str): Cột cần xóa outliers (default='amount').
        iqr_multiplier (float): Hệ số nhân IQR (default=1.5).
        
    Returns:
        pd.DataFrame: DataFrame sau khi xóa outliers.
    """
    try:
        df = df.copy()

        if column not in df.columns:
            raise ValueError(f"Cột '{column}' không tồn tại")

        # Tính Q1, Q3, IQR
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        # Tính ngưỡng
        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR

        # Đếm outliers
        outliers_count = len(df[(df[column] < lower_bound) | (df[column] > upper_bound)])
        
        if outliers_count > 0:
            print(f"⚠️  Phát hiện {outliers_count} outliers trong cột '{column}'")
            print(f"   Ngưỡng: [{lower_bound:.0f}, {upper_bound:.0f}]")

        # Lọc
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

        return df
        
    except Exception as exc:
        print(f"❌ Lỗi xóa outliers: {exc}")
        return df


def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Xử lý các giá trị thiếu trong dữ liệu.
    
    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu.
        strategy (str): Chiến lược xử lý:
            - 'drop': Xóa dòng có giá trị thiếu
            - 'forward_fill': Điền giá trị từ dòng trước
            - 'mean': Điền giá trị trung bình (chỉ cho số)
            
    Returns:
        pd.DataFrame: DataFrame sau xử lý.
    """
    try:
        df = df.copy()
        initial_count = len(df)

        if strategy == 'drop':
            df = df.dropna()
        elif strategy == 'forward_fill':
            df = df.fillna(method='ffill').fillna(method='bfill')
        elif strategy == 'mean':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            df = df.dropna()

        removed_count = initial_count - len(df)
        if removed_count > 0:
            print(f"⚠️  Xóa {removed_count} dòng có giá trị thiếu")

        return df
        
    except Exception as exc:
        print(f"❌ Lỗi xử lý giá trị thiếu: {exc}")
        return df


def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Kiểm tra và chuẩn hóa kiểu dữ liệu.
    
    Args:
        df (pd.DataFrame): DataFrame cần kiểm tra.
        
    Returns:
        pd.DataFrame: DataFrame với kiểu dữ liệu đã chuẩn hóa.
    """
    try:
        df = df.copy()

        # Chuẩn hóa các cột chung
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        if 'transaction_type' in df.columns:
            df['transaction_type'] = df['transaction_type'].astype('string')
        
        if 'auto_category' in df.columns:
            df['auto_category'] = df['auto_category'].astype('string')

        return df
        
    except Exception as exc:
        print(f"❌ Lỗi xác thực kiểu dữ liệu: {exc}")
        return df


def clean_data(df: pd.DataFrame, remove_outliers: bool = True) -> pd.DataFrame:
    """
    Pipeline làm sạch dữ liệu gồm các bước chuẩn hóa.
    
    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu thô.
        remove_outliers (bool): Có xóa outliers không (default=True).
        
    Returns:
        pd.DataFrame: DataFrame đã được làm sạch và chuẩn hóa.
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng hoặc None")
            return df

        print("\n🧹 BẮT ĐẦU QUI TRÌNH LÀM SẠCH DỮ LIỆU")
        print("-" * 50)
        
        initial_count = len(df)

        # Bước 1: Chuẩn hóa cột
        df = standardize_columns(df)
        print("✓ Chuẩn hóa tên cột")

        # Bước 2: Chuẩn hóa kiểu dữ liệu
        df = validate_data_types(df)
        print("✓ Xác thực kiểu dữ liệu")

        # Bước 3: Chuẩn hóa giá trị
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = normalize_amount(df)
        print("✓ Chuẩn hóa số tiền")

        # Bước 4: Xóa duplicates
        dup_count = df.duplicated().sum()
        df = df.drop_duplicates()
        if dup_count > 0:
            print(f"✓ Xóa {dup_count} dòng trùng lặp")

        # Bước 5: Xử lý giá trị thiếu
        df = handle_missing_values(df, strategy='drop')
        print("✓ Xử lý giá trị thiếu")

        # Bước 6: Xóa outliers (tùy chọn)
        if remove_outliers:
            df = remove_outliers_iqr(df, column='amount', iqr_multiplier=2.0)
            print("✓ Xóa outliers")

        # Bước 7: Thêm date features
        df = add_date_features(df)
        print("✓ Thêm date features")

        # Reset index
        df = df.reset_index(drop=True)

        # Kết quả
        print("-" * 50)
        removed_count = initial_count - len(df)
        print(f"✅ Hoàn thành: {len(df)} dòng hợp lệ ({removed_count} dòng bị loại bỏ)")
        print()

        return df
        
    except Exception as exc:
        print(f"❌ Lỗi khi làm sạch dữ liệu: {exc}")
        return df