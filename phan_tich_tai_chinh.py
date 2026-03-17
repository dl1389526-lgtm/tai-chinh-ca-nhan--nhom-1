import pandas as pd
from modules.du_bao_so_du import du_bao_so_du
from modules.phan_tich_pareto import analyze_pareto_by_category, analyze_pareto_by_month, print_pareto_insights
from modules.truc_quan_du_lieu import visualize_data


def tinh_ty_le_tiet_kiem(df: pd.DataFrame) -> float:
    """
    Tính tỷ lệ tiết kiệm từ dữ liệu giao dịch.
    
    Công thức: Tỷ lệ tiết kiệm (%) = (Thu nhập - Chi tiêu) / Thu nhập * 100
    
    Args:
        df (pd.DataFrame): DataFrame chứa 'amount' và 'auto_category'.
        
    Returns:
        float: Tỷ lệ tiết kiệm dưới dạng phần trăm. Trả về 0 nếu lỗi.
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng")
            return 0.0

        if 'amount' not in df.columns or 'auto_category' not in df.columns:
            raise ValueError("DataFrame phải có cột 'amount' và 'auto_category'")

        # Tính tổng thu nhập (Income)
        tong_thu_nhap = df[df['auto_category'] == 'Income']['amount'].sum()
        
        # Tính tổng chi tiêu (tất cả chi tiêu khác Income)
        chi_tieu_df = df[df['auto_category'] != 'Income']
        tong_chi_tieu = chi_tieu_df[chi_tieu_df['amount'] < 0]['amount'].sum()
        tong_chi_tieu = abs(tong_chi_tieu)  # Chuyển âm thành dương để tính

        # Xử lý trường hợp không có thu nhập
        if tong_thu_nhap <= 0:
            if tong_chi_tieu > 0:
                print("⚠️  Không có thu nhập nhưng có chi tiêu")
            return 0.0

        # Tính tiền tiết kiệm thực tế
        so_tien_tiet_kiem = tong_thu_nhap - tong_chi_tieu

        # Tính tỷ lệ
        ty_le = (so_tien_tiet_kiem / tong_thu_nhap) * 100

        return max(ty_le, 0.0)  # Đảm bảo không âm
        
    except Exception as exc:
        print(f"❌ Lỗi tính tỷ lệ tiết kiệm: {exc}")
        return 0.0


def bao_cao_tai_chinh(df: pd.DataFrame) -> None:
    """
    Tạo báo cáo tài chính tổng hợp với các chỉ số chính.
    
    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch.
    """
    try:
        if df is None or df.empty:
            print("⚠️  Không có dữ liệu để báo cáo")
            return

        print("\n" + "="*50)
        print("📊 BÁO CÁO TÀI CHÍNH")
        print("="*50)

        # 1. Tính tỷ lệ tiết kiệm
        ty_le = tinh_ty_le_tiet_kiem(df)
        print(f"\n💰 Tỷ lệ tiết kiệm: {ty_le:.2f}%")

        # 2. Tính tổng thu nhập và chi tiêu
        tong_thu_nhap = df[df['auto_category'] == 'Income']['amount'].sum()
        chi_tieu_df = df[df['auto_category'] != 'Income']
        tong_chi_tieu = abs(chi_tieu_df[chi_tieu_df['amount'] < 0]['amount'].sum())
        so_du = tong_thu_nhap - tong_chi_tieu

        print(f"📈 Tổng thu nhập: {tong_thu_nhap:,.0f} VND")
        print(f"📉 Tổng chi tiêu: {tong_chi_tieu:,.0f} VND")
        print(f"💵 Số dư hiện tại: {so_du:,.0f} VND")

        # 3. Dự báo số dư
        print("\n📋 Dự báo số dư 12 tháng tới:")
        du_bao = du_bao_so_du(df)
        
        if not du_bao.empty:
            print(f"Dự báo số dư cuối tháng thứ 12: {du_bao['forecast_balance'].iloc[-1]:,.0f} VND")
        else:
            print("⚠️  Không thể dự báo (dữ liệu không đủ)")

        # 4. Phân tích Pareto
        print("\n🎯 PHÂN TÍCH PARETO (20/80 RULE):")
        pareto_category = analyze_pareto_by_category(df)
        if not pareto_category.empty:
            print_pareto_insights(pareto_category, "category")
        
        pareto_month = analyze_pareto_by_month(df)
        if not pareto_month.empty:
            print_pareto_insights(pareto_month, "month")

        # 5. Thống kê chi tiêu theo tháng
        thong_ke_thang_tieu(df)

        # 6. Insights tổng hợp
        print("\n" + "="*50)
        print("💡 INSIGHT & KHUYẾN NGHỊ:")
        if ty_le > 30:
            print("✅ Tài chính XUẤT SẮC - Bạn tiết kiệm được >30%")
        elif ty_le > 20:
            print("✅ Tài chính TỐT - Bạn tiết kiệm được >20%")
        elif ty_le > 10:
            print("⚠️  Tài chính BÌNH THƯỜNG - Nên tối ưu chi tiêu")
        elif ty_le > 0:
            print("⚠️  Tài chính CẦN CẢI THIỆN - Hãy giảm chi tiêu")
        else:
            print("🔴 CẢNH BÁO - Chi tiêu vượt thu nhập!")

        print("="*50 + "\n")
        
    except Exception as exc:
        print(f"❌ Lỗi tạo báo cáo: {exc}")


def thong_ke_thang_tieu(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính thống kê chi tiêu theo tháng (moyenne, min, max, std).
    
    Args:
        df (pd.DataFrame): DataFrame chứa 'date' và 'amount'.
        
    Returns:
        pd.DataFrame: Thống kê chi tiêu theo tháng.
    """
    try:
        if df is None or df.empty:
            print("⚠️  DataFrame rỗng")
            return pd.DataFrame()

        if 'date' not in df.columns or 'amount' not in df.columns:
            raise ValueError("DataFrame phải có cột 'date' và 'amount'")

        # Lọc chi tiêu
        spending_df = df[df['amount'] < 0].copy()
        
        if spending_df.empty:
            print("⚠️  Không có chi tiêu nào")
            return pd.DataFrame()

        # Chuẩn hóa date
        spending_df['date'] = pd.to_datetime(spending_df['date'], errors='coerce')
        spending_df = spending_df.dropna(subset=['date'])

        # Tính tổng chi tiêu theo tháng
        spending_df['year_month'] = spending_df['date'].dt.to_period('M')
        spending_df['amount_abs'] = spending_df['amount'].abs()

        monthly_stats = spending_df.groupby('year_month')['amount_abs'].agg([
            ('tong_chi_tieu', 'sum'),
            ('trung_binh_giao_dich', 'mean'),
            ('chi_tieu_min', 'min'),
            ('chi_tieu_max', 'max'),
            ('so_giao_dich', 'count'),
            ('do_lech_chuan', 'std')
        ]).reset_index()

        monthly_stats.columns = [
            'year_month', 'tong_chi_tieu', 'trung_binh_giao_dich',
            'chi_tieu_min', 'chi_tieu_max', 'so_giao_dich', 'do_lech_chuan'
        ]

        monthly_stats['year_month'] = monthly_stats['year_month'].astype(str)

        # In thống kê
        print("\n📈 THỐNG KÊ CHI TIÊU THEO THÁNG:")
        print("\n{:<12} {:<15} {:<15} {:<10} {:<10} {:<10} {:<12}".format(
            "Tháng", "Tổng (VND)", "Trung bình", "Min", "Max", "Số GD", "Độ lệch"
        ))
        print("-" * 95)

        for _, row in monthly_stats.iterrows():
            print("{:<12} {:>13,.0f} {:>13,.0f} {:>8,.0f} {:>8,.0f} {:>8.0f} {:>10,.0f}".format(
                row['year_month'],
                row['tong_chi_tieu'],
                row['trung_binh_giao_dich'],
                row['chi_tieu_min'],
                row['chi_tieu_max'],
                row['so_giao_dich'],
                row['do_lech_chuan'] if pd.notna(row['do_lech_chuan']) else 0
            ))

        # Tính trung bình chung
        print("-" * 95)
        chi_tieu_tb_chung = monthly_stats['tong_chi_tieu'].mean()
        chi_tieu_max_thang = monthly_stats['tong_chi_tieu'].max()
        chi_tieu_min_thang = monthly_stats['tong_chi_tieu'].min()
        
        print(f"⏱️  Trung bình/tháng: {chi_tieu_tb_chung:,.0f} VND")
        print(f"📊 Tháng cao điểm: {chi_tieu_max_thang:,.0f} VND (+{((chi_tieu_max_thang/chi_tieu_tb_chung - 1)*100):.1f}%)")
        print(f"📊 Tháng thấp điểm: {chi_tieu_min_thang:,.0f} VND ({((chi_tieu_min_thang/chi_tieu_tb_chung - 1)*100):.1f}%)")
        
        return monthly_stats
        
    except Exception as exc:
        print(f"❌ Lỗi thống kê chi tiêu: {exc}")
        return pd.DataFrame()