import numpy as np
import pandas as pd


def compute_monthly_cashflow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính dòng tiền ròng theo từng tháng.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch
                           phải có cột 'date' và 'amount'.

    Returns:
        pd.DataFrame: DataFrame gồm cột 'year_month' và 'net_flow'.
        
    Raises:
        ValueError: Nếu DataFrame thiếu cột 'date' hoặc 'amount'.
    """
    try:
        df = df.copy()

        if "date" not in df.columns or "amount" not in df.columns:
            raise ValueError("DataFrame phải có cột 'date' và 'amount'")

        # Chuẩn hóa datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Loại bỏ dữ liệu lỗi
        df = df.dropna(subset=["date", "amount"])
        
        if df.empty:
            raise ValueError("Không có dữ liệu hợp lệ sau khi chuẩn hóa")

        # Tạo cột tháng
        df["year_month"] = df["date"].dt.to_period("M")

        # Tính tổng dòng tiền theo tháng
        monthly = df.groupby("year_month")["amount"].sum().reset_index()

        monthly = monthly.rename(columns={"amount": "net_flow"})

        monthly["year_month"] = monthly["year_month"].astype(str)

        return monthly
        
    except Exception as exc:
        print(f"❌ Lỗi tính dòng tiền theo tháng: {exc}")
        return pd.DataFrame()


def forecast_balance(monthly_cashflow: pd.DataFrame, months_ahead: int = 12) -> pd.DataFrame:
    """
    Dự báo số dư tài khoản trong tương lai bằng hồi quy tuyến tính.

    Args:
        monthly_cashflow (pd.DataFrame): DataFrame chứa 'year_month' và 'net_flow'
        months_ahead (int): Số tháng dự báo (default=12)

    Returns:
        pd.DataFrame: DataFrame gồm 'year_month' và 'forecast_balance'.
        
    Raises:
        ValueError: Nếu dữ liệu không đủ hoặc cột bị thiếu.
    """
    try:
        df = monthly_cashflow.copy()

        if "net_flow" not in df.columns:
            raise ValueError("monthly_cashflow phải có cột 'net_flow'")

        if len(df) < 2:
            raise ValueError("Cần ít nhất 2 tháng dữ liệu để dự báo")

        # Tính số dư tích lũy
        df["cumulative_balance"] = df["net_flow"].cumsum()

        # Chuẩn bị dữ liệu cho hồi quy
        x = np.arange(len(df))
        y = df["cumulative_balance"].values

        # Hồi quy tuyến tính y = ax + b
        slope, intercept = np.polyfit(x, y, 1)

        # Tạo dữ liệu tương lai
        future_x = np.arange(len(x), len(x) + months_ahead)
        forecast_balance = slope * future_x + intercept

        # Tạo danh sách tháng tương lai
        last_month = pd.to_datetime(df["year_month"].iloc[-1])
        
        future_months = pd.date_range(
            start=last_month + pd.offsets.MonthBegin(),
            periods=months_ahead,
            freq="MS"
        ).to_period("M").astype(str)

        forecast_df = pd.DataFrame({
            "year_month": future_months,
            "forecast_balance": forecast_balance
        })

        return forecast_df
        
    except Exception as exc:
        print(f"❌ Lỗi dự báo số dư: {exc}")
        return pd.DataFrame()


def du_bao_so_du(df: pd.DataFrame, months_ahead: int = 12) -> pd.DataFrame:
    """
    Pipeline dự báo số dư tài khoản.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch.
        months_ahead (int): Số tháng dự báo (default=12).

    Returns:
        pd.DataFrame: DataFrame chứa dự báo số dư hoặc DataFrame rỗng nếu lỗi.
    """
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame không được rỗng")

        monthly_cashflow = compute_monthly_cashflow(df)
        
        if monthly_cashflow.empty:
            raise ValueError("Không thể tính dòng tiền hàng tháng")

        forecast_df = forecast_balance(monthly_cashflow, months_ahead)
        
        if forecast_df.empty:
            raise ValueError("Không thể dự báo số dư")

        return forecast_df
        
    except Exception as exc:
        print(f"❌ Lỗi pipeline dự báo: {exc}")
        return pd.DataFrame()