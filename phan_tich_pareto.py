"""
Module phân tích Pareto (20/80 Rule) cho chi tiêu.
Giúp xác định 20% danh mục mang lại 80% chi tiêu.
"""

import pandas as pd
import numpy as np


def analyze_pareto_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Phân tích Pareto theo danh mục chi tiêu.
    
    Câu hỏi: Danh mục nào chiếm 80% chi tiêu?
    
    Args:
        df (pd.DataFrame): DataFrame chứa 'auto_category' và 'amount'.
        
    Returns:
        pd.DataFrame: DataFrame với cột:
            - auto_category: Danh mục
            - total_spending: Tổng chi tiêu
            - percentage: Phần trăm của tổng
            - cumulative_percentage: Tích lũy %
            - is_pareto: True nếu nằm trong 80% chi tiêu
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng")
            return pd.DataFrame()

        if 'auto_category' not in df.columns or 'amount' not in df.columns:
            raise ValueError("DataFrame phải có cột 'auto_category' và 'amount'")

        # Lọc chỉ chi tiêu
        spending_df = df[df['amount'] < 0].copy()
        
        if spending_df.empty:
            print("⚠️  Không có chi tiêu nào")
            return pd.DataFrame()

        # Tính tổng chi tiêu theo danh mục
        category_spending = (
            spending_df.groupby('auto_category')['amount']
            .sum()
            .abs()
            .reset_index()
            .sort_values('amount', ascending=False)
        )
        
        category_spending.columns = ['auto_category', 'total_spending']

        # Tính phần trăm
        total = category_spending['total_spending'].sum()
        category_spending['percentage'] = (
            category_spending['total_spending'] / total * 100
        )

        # Tính tích lũy
        category_spending['cumulative_percentage'] = (
            category_spending['percentage'].cumsum()
        )

        # Đánh dấu Pareto (80% tích lũy)
        category_spending['is_pareto'] = (
            category_spending['cumulative_percentage'] <= 80
        )

        return category_spending
        
    except Exception as exc:
        print(f"❌ Lỗi phân tích Pareto theo danh mục: {exc}")
        return pd.DataFrame()


def analyze_pareto_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Phân tích Pareto theo tháng chi tiêu.
    
    Câu hỏi: Tháng nào chiếm 80% chi tiêu?
    
    Args:
        df (pd.DataFrame): DataFrame chứa 'date' và 'amount'.
        
    Returns:
        pd.DataFrame: DataFrame với cột:
            - year_month: Tháng
            - total_spending: Tổng chi tiêu
            - percentage: Phần trăm của tổng
            - cumulative_percentage: Tích lũy %
            - is_pareto: True nếu nằm trong 80% chi tiêu
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng")
            return pd.DataFrame()

        if 'date' not in df.columns or 'amount' not in df.columns:
            raise ValueError("DataFrame phải có cột 'date' và 'amount'")

        # Lọc chỉ chi tiêu
        spending_df = df[df['amount'] < 0].copy()
        
        if spending_df.empty:
            print("⚠️  Không có chi tiêu nào")
            return pd.DataFrame()

        # Chuẩn hóa date
        spending_df['date'] = pd.to_datetime(spending_df['date'], errors='coerce')
        spending_df = spending_df.dropna(subset=['date'])

        # Tính tổng chi tiêu theo tháng
        spending_df['year_month'] = spending_df['date'].dt.to_period('M')
        
        month_spending = (
            spending_df.groupby('year_month')['amount']
            .sum()
            .abs()
            .reset_index()
            .sort_values('amount', ascending=False)
        )
        
        month_spending.columns = ['year_month', 'total_spending']
        month_spending['year_month'] = month_spending['year_month'].astype(str)

        # Tính phần trăm
        total = month_spending['total_spending'].sum()
        month_spending['percentage'] = (
            month_spending['total_spending'] / total * 100
        )

        # Tính tích lũy
        month_spending['cumulative_percentage'] = (
            month_spending['percentage'].cumsum()
        )

        # Đánh dấu Pareto (80% tích lũy)
        month_spending['is_pareto'] = (
            month_spending['cumulative_percentage'] <= 80
        )

        return month_spending
        
    except Exception as exc:
        print(f"❌ Lỗi phân tích Pareto theo tháng: {exc}")
        return pd.DataFrame()


def print_pareto_insights(pareto_df: pd.DataFrame, analysis_type: str = "category") -> None:
    """
    In ra insights từ phân tích Pareto.
    
    Args:
        pareto_df (pd.DataFrame): Kết quả từ analyze_pareto_by_category hoặc analyze_pareto_by_month
        analysis_type (str): "category" hoặc "month"
    """
    try:
        if pareto_df is None or pareto_df.empty:
            print("⚠️  Không có dữ liệu Pareto")
            return

        print("\n" + "="*60)
        if analysis_type == "category":
            print("📊 PHÂN TÍCH PARETO - CHI TIÊU THEO DANH MỤC (20/80 RULE)")
        else:
            print("📊 PHÂN TÍCH PARETO - CHI TIÊU THEO THÁNG (20/80 RULE)")
        print("="*60)

        # Lấy dòng Pareto
        pareto_items = pareto_df[pareto_df['is_pareto'] == True]
        
        if pareto_items.empty:
            print("⚠️  Không có chi tiêu nào")
            return

        print(f"\n✅ {len(pareto_items)} mục chiếm 80% chi tiêu:")
        print("\n{:<20} {:<15} {:<12} {:<15}".format(
            "Danh mục" if analysis_type == "category" else "Tháng",
            "Chi tiêu (VND)",
            "%",
            "Tích lũy %"
        ))
        print("-" * 60)

        for _, row in pareto_items.iterrows():
            key = row.iloc[0]  # auto_category hoặc year_month
            spending = row['total_spending']
            pct = row['percentage']
            cum_pct = row['cumulative_percentage']
            
            print("{:<20} {:>13,.0f} {:>10.1f}% {:>13.1f}%".format(
                str(key)[:20], spending, pct, cum_pct
            ))

        # Insights
        print("\n" + "="*60)
        print("💡 INSIGHTS:")
        
        total_items = len(pareto_df)
        pareto_count = len(pareto_items)
        pareto_percentage = (pareto_count / total_items * 100) if total_items > 0 else 0
        
        print(f"• {pareto_count}/{total_items} mục ({pareto_percentage:.1f}%) chiếm 80% chi tiêu")
        
        if analysis_type == "category":
            print(f"• Hãy tập trung tối ưu hóa {pareto_count} danh mục này")
            print(f"• Giảm 1% ở danh mục này = tiết kiệm {pareto_df['total_spending'].iloc[0]/100:.0f} VND/tháng")
        else:
            print(f"• Những tháng cao điểm: {', '.join(pareto_items.iloc[:3]['year_month'].tolist())}")
            print(f"• Hãy lên kế hoạch chi tiêu tốt hơn cho những tháng này")
        
        print("="*60 + "\n")
        
    except Exception as exc:
        print(f"❌ Lỗi in Pareto insights: {exc}")
