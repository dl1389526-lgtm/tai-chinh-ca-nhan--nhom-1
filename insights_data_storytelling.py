"""
Module tạo insights và giải thích kết quả phân tích tài chính.
Data Storytelling - biến dữ liệu thành câu chuyện có ý nghĩa với AI insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta


def generate_financial_insights(df: pd.DataFrame) -> Dict[str, str]:
    """
    Tạo insights tự động từ dữ liệu tài chính với AI analysis.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch với các cột:
            - date: Ngày giao dịch
            - amount: Số tiền (dương = thu, âm = chi)
            - auto_category: Danh mục tự động phân loại

    Returns:
        Dict[str, str]: Dictionary chứa các insights theo chủ đề:
            - overview: Tổng quan tài chính
            - spending_patterns: Mẫu chi tiêu
            - trends: Xu hướng theo thời gian
            - pareto: Phân tích Pareto
            - recommendations: Khuyến nghị AI
            - risk_assessment: Đánh giá rủi ro
            - financial_health: Sức khỏe tài chính

    Raises:
        ValueError: Nếu DataFrame không có cấu trúc phù hợp
    """
    insights: Dict[str, str] = {}

    try:
        if df is None or df.empty:
            return {"error": "Không có dữ liệu để phân tích"}

        # Validate required columns
        required_cols = ['date', 'amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return {"error": f"Thiếu các cột bắt buộc: {missing_cols}"}

        # 1. Phân tích tổng quan
        insights.update(analyze_overview(df))

        # 2. Phân tích chi tiêu
        insights.update(analyze_spending_patterns(df))

        # 3. Phân tích xu hướng
        insights.update(analyze_trends(df))

        # 4. Phân tích Pareto
        insights.update(analyze_pareto_insights(df))

        # 5. AI Khuyến nghị thông minh
        insights.update(generate_ai_recommendations(df))

        # 6. Đánh giá rủi ro
        insights.update(assess_financial_risks(df))

        # 7. Sức khỏe tài chính
        insights.update(analyze_financial_health(df))

        return insights

    except Exception as exc:
        return {"error": f"Lỗi tạo insights: {str(exc)}"}


def analyze_overview(df: pd.DataFrame) -> Dict[str, str]:
    """Phân tích tổng quan tài chính với các chỉ số chính."""
    insights: Dict[str, str] = {}

    try:
        total_income: float = df[df['amount'] > 0]['amount'].sum()
        total_expense: float = abs(df[df['amount'] < 0]['amount'].sum())
        net_balance: float = total_income - total_expense
        savings_rate: float = (net_balance / total_income * 100) if total_income > 0 else 0

        df_clean = _prepare_date_column(df.copy())

        if not df_clean.empty:
            months: int = df_clean['date'].dt.to_period('M').nunique()
            avg_monthly_expense: float = total_expense / months if months > 0 else 0
            avg_monthly_income: float = total_income / months if months > 0 else 0

            monthly_balance = df_clean.groupby(df_clean['date'].dt.to_period('M'))['amount'].sum()
            balance_volatility = monthly_balance.std() if len(monthly_balance) > 1 else 0

            insights['overview'] = f"""
TỔNG QUAN TÀI CHÍNH
- Thu nhập: {total_income:,.0f} VND ({avg_monthly_income:,.0f} VND/tháng)
- Chi tiêu: {total_expense:,.0f} VND ({avg_monthly_expense:,.0f} VND/tháng)
- Số dư: {net_balance:,.0f} VND
- Tỷ lệ tiết kiệm: {savings_rate:.1f}%
- Số tháng dữ liệu: {months}
- Biến động số dư: {balance_volatility:,.0f} VND
"""

        return insights

    except Exception as exc:
        return {"overview_error": f"Lỗi phân tích tổng quan: {str(exc)}"}


def analyze_spending_patterns(df: pd.DataFrame) -> Dict[str, str]:
    """Phân tích mẫu chi tiêu chi tiết."""
    insights: Dict[str, str] = {}

    try:
        spending = df[df['amount'] < 0].copy()
        if spending.empty:
            return {"spending_patterns": "Không có dữ liệu chi tiêu"}

        spending['amount'] = spending['amount'].abs()
        spending = _prepare_date_column(spending)

        top_categories = (
            spending.groupby('auto_category')['amount']
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        spending['weekday'] = spending['date'].dt.day_name()
        weekday_spending = spending.groupby('weekday')['amount'].sum().sort_values(ascending=False)

        if 'date' in spending.columns and spending['date'].dt.hour.notna().any():
            spending['hour'] = spending['date'].dt.hour
            peak_hour = spending.groupby('hour')['amount'].sum().idxmax()
        else:
            peak_hour = "N/A"

        avg_transactions_per_day = len(spending) / spending['date'].dt.date.nunique() if spending['date'].dt.date.nunique() > 0 else 0
        category_frequency = spending['auto_category'].value_counts().head(3)

        insights['spending_patterns'] = f"""
MẪU CHI TIÊU THÔNG MINH
- Top 3 danh mục chi tiêu:
  1. {top_categories.index[0]}: {top_categories.iloc[0]:,.0f} VND
  2. {top_categories.index[1] if len(top_categories) > 1 else 'N/A'}: {top_categories.iloc[1]:,.0f} VND
  3. {top_categories.index[2] if len(top_categories) > 2 else 'N/A'}: {top_categories.iloc[2]:,.0f} VND
- Ngày chi tiêu nhiều nhất: {weekday_spending.index[0]} 
- Giờ chi tiêu cao điểm: {peak_hour}h
- Số giao dịch trung bình/ngày: {avg_transactions_per_day:.1f}
- Danh mục thường xuyên nhất: {category_frequency.index[0]} 
"""

        return insights

    except Exception as exc:
        return {"spending_patterns_error": f"Lỗi phân tích chi tiêu: {str(exc)}"}


def analyze_trends(df: pd.DataFrame) -> Dict[str, str]:
    """Phân tích xu hướng chi tiêu."""
    insights: Dict[str, str] = {}

    try:
        df_clean = _prepare_date_column(df.copy())

        if df_clean.empty:
            return {"trends": "Không đủ dữ liệu để phân tích xu hướng"}

        monthly = df_clean.groupby(df_clean['date'].dt.to_period('M'))['amount'].sum()

        if len(monthly) >= 2:
            x = np.arange(len(monthly))
            slope, intercept = np.polyfit(x, monthly.values, 1)

            trend = "tăng" if slope > 0 else "giảm"
            trend_amount = abs(slope)

            y_pred = slope * x + intercept
            r_squared = np.corrcoef(monthly.values, y_pred)[0, 1] ** 2

            max_month = monthly.idxmax()
            min_month = monthly.idxmin()

            monthly_expense = df_clean[df_clean['amount'] < 0].groupby(df_clean['date'].dt.month)['amount'].sum().abs()
            seasonal_peak = monthly_expense.idxmax() if not monthly_expense.empty else "N/A"

            next_month_forecast = slope * (len(monthly)) + intercept

            insights['trends'] = f"""
XU HƯỚNG CHI TIÊU THÔNG MINH
- Xu hướng: Chi tiêu {trend} {trend_amount:.0f} VND/tháng
- Độ tin cậy: {r_squared:.3f}
- Tháng chi tiêu cao nhất: {max_month}
- Tháng chi tiêu thấp nhất: {min_month}
- Biên độ chi tiêu: {((monthly.max() - monthly.min()) / monthly.min() * 100):.1f}%
- Dự báo tháng tiếp theo: {next_month_forecast:,.0f} VND
"""

        return insights

    except Exception as exc:
        return {"trends_error": f"Lỗi phân tích xu hướng: {str(exc)}"}


def analyze_pareto_insights(df: pd.DataFrame) -> Dict[str, str]:
    """Phân tích Pareto."""
    insights: Dict[str, str] = {}

    try:
        spending = df[df['amount'] < 0].copy()
        if spending.empty:
            return {"pareto": "Không có dữ liệu chi tiêu"}

        spending['amount'] = spending['amount'].abs()

        category_total = spending.groupby('auto_category')['amount'].sum().sort_values(ascending=False)
        category_cumsum = category_total.cumsum()
        category_cumsum_pct = category_cumsum / category_total.sum() * 100

        pareto_categories = category_cumsum_pct[category_cumsum_pct <= 80]

        pareto_ratio = len(pareto_categories) / len(category_total) * 100
        concentration_ratio = category_cumsum_pct.iloc[len(pareto_categories)-1] if len(pareto_categories) > 0 else 0

        potential_savings = category_total.iloc[len(pareto_categories):].sum() * 0.1

        insights['pareto'] = f"""
PHÂN TÍCH PARETO (20/80 RULE)
- {len(pareto_categories)}/{len(category_total)} danh mục chiếm {concentration_ratio:.1f}% chi tiêu
- Danh mục quan trọng: {', '.join(pareto_categories.index.tolist())}
- Cơ hội tiết kiệm: {potential_savings:,.0f} VND
- Chiến lược: Tập trung tối ưu hóa {len(pareto_categories)} danh mục chính
"""

        return insights

    except Exception as exc:
        return {"pareto_error": f"Lỗi phân tích Pareto: {str(exc)}"}


def generate_ai_recommendations(df: pd.DataFrame) -> Dict[str, str]:
    """Tạo khuyến nghị thông minh."""
    recommendations: List[str] = []

    try:
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expense = abs(df[df['amount'] < 0]['amount'].sum())
        savings_rate = (total_income - total_expense) / total_income * 100 if total_income > 0 else 0

        if savings_rate < 0:
            recommendations.append("CẢNH BÁO: Chi tiêu vượt thu nhập! Cần cắt giảm chi tiêu ngay lập tức.")
        elif savings_rate < 10:
            recommendations.append("CẢNH BÁO: Tỷ lệ tiết kiệm quá thấp. Mục tiêu tối thiểu 20%.")
        elif savings_rate < 20:
            recommendations.append("TỐT: Tỷ lệ tiết kiệm ở mức khả. Tiếp tục duy trì và tăng dần.")
        else:
            recommendations.append("XUẤT SẮC: Tỷ lệ tiết kiệm rất tốt! Bạn đang quản lý tài chính xuất sắc.")

        spending = df[df['amount'] < 0].copy()
        if not spending.empty:
            spending['amount'] = spending['amount'].abs()
            top_category = spending.groupby('auto_category')['amount'].sum().idxmax()
            top_amount = spending.groupby('auto_category')['amount'].sum().max()
            top_percentage = top_amount / total_expense * 100

            if top_percentage > 40:
                recommendations.append(f"TIÊU ĐIỂM: {top_category} chiếm {top_percentage:.1f}% chi tiêu")

        return {"recommendations": "\n".join(recommendations) if recommendations else "Tài chính ổn định"}

    except Exception as exc:
        return {"recommendations_error": f"Lỗi tạo khuyến nghị: {str(exc)}"}


def assess_financial_risks(df: pd.DataFrame) -> Dict[str, str]:
    """Đánh giá rủi ro tài chính."""
    risks: List[str] = []
    risk_level = "LOW"

    try:
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expense = abs(df[df['amount'] < 0]['amount'].sum())

        if total_expense > total_income:
            risks.append("CẤP ĐỘ CAO: Chi tiêu vượt thu nhập")
            risk_level = "HIGH"

        savings_rate = (total_income - total_expense) / total_income * 100 if total_income > 0 else 0
        if savings_rate < 10:
            risks.append("CẤP ĐỘ TRUNG BÌNH: Tỷ lệ tiết kiệm thấp")
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        risk_assessment = f"""
ĐÁNH GIÁ RỦI RO TÀI CHÍNH
- Mức độ rủi ro: {risk_level}
- Các rủi ro phát hiện:
"""

        if risks:
            for risk in risks:
                risk_assessment += f"  {risk}\n"
        else:
            risk_assessment += "  Không phát hiện rủi ro\n"

        return {"risk_assessment": risk_assessment}

    except Exception as exc:
        return {"risk_assessment_error": f"Lỗi đánh giá rủi ro: {str(exc)}"}


def analyze_financial_health(df: pd.DataFrame) -> Dict[str, str]:
    """Phân tích sức khỏe tài chính."""
    try:
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expense = abs(df[df['amount'] < 0]['amount'].sum())
        savings_rate = (total_income - total_expense) / total_income * 100 if total_income > 0 else 0

        health_score = 0

        if savings_rate >= 30:
            health_score += 40
        elif savings_rate >= 20:
            health_score += 30
        elif savings_rate >= 10:
            health_score += 20
        elif savings_rate >= 0:
            health_score += 10

        df_clean = _prepare_date_column(df.copy())
        if not df_clean.empty:
            monthly = df_clean.groupby(df_clean['date'].dt.to_period('M'))['amount'].sum()
            if len(monthly) > 1:
                volatility = monthly.std() / monthly.mean()
                if volatility < 0.2:
                    health_score += 30
                elif volatility < 0.4:
                    health_score += 20
                elif volatility < 0.6:
                    health_score += 10

        spending = df[df['amount'] < 0].copy()
        if not spending.empty:
            spending['amount'] = spending['amount'].abs()
            num_categories = len(spending['auto_category'].unique())
            if num_categories >= 5:
                health_score += 20
            elif num_categories >= 3:
                health_score += 15
            elif num_categories >= 2:
                health_score += 10

        if savings_rate >= 15:
            health_score += 10
        elif savings_rate >= 5:
            health_score += 5

        if health_score >= 80:
            health_level = "Xuất sắc"
        elif health_score >= 60:
            health_level = "Tốt"
        elif health_score >= 40:
            health_level = "Trung bình"
        else:
            health_level = "Cần cải thiện"

        health_analysis = f"""
SỨC KHỎE TÀI CHÍNH
- Điểm số: {health_score}/100
- Mức độ: {health_level}
- Tỷ lệ tiết kiệm: {savings_rate:.1f}%
"""

        return {"financial_health": health_analysis}

    except Exception as exc:
        return {"financial_health_error": f"Lỗi phân tích sức khỏe: {str(exc)}"}


def _prepare_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Chuan hoa cot date."""
    try:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    except Exception:
        return pd.DataFrame()


def print_insights(insights: Dict[str, str]) -> None:
    """In ra insights."""
    try:
        print("\n" + "="*80)
        print("PHÂN TÍCH THÔNG MINH - AI INSIGHTS")
        print("="*80)

        order = ['overview', 'spending_patterns', 'trends', 'pareto',
                'recommendations', 'risk_assessment', 'financial_health']

        for key in order:
            if key in insights:
                print(f"\n{insights[key]}")

        for key, value in insights.items():
            if key not in order and not key.endswith("_error"):
                print(f"\n{value}")

        print("\n" + "="*80)
        print("HOÀN THÀNH PHÂN TÍCH AI INSIGHTS")
        print("="*80)

    except Exception as exc:
        print(f"Lỗi in insights: {str(exc)}")


def create_data_story(df: pd.DataFrame) -> str:
    """Tạo câu chuyện tài chính."""
    try:
        insights = generate_financial_insights(df)

        story = f"""
CÂU CHUYỆN TÀI CHÍNH CỦA BẠN

{insights.get('overview', '')}

{insights.get('spending_patterns', '')}

{insights.get('trends', '')}

{insights.get('pareto', '')}

{insights.get('recommendations', '')}

{insights.get('risk_assessment', '')}

{insights.get('financial_health', '')}
"""

        return story

    except Exception as exc:
        return f"Không thể tạo câu chuyện: {str(exc)}"
