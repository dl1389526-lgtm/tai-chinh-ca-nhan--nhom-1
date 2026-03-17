"File chạy chính của chương trình quản lý tài chính cá nhân"
import pandas as pd
from modules.nhap_du_lieu import doc_du_lieu, nhap_giao_dich
from modules.lam_sach_du_lieu import clean_data
from modules.phan_loai_chi_tieu import apply_auto_classification
from modules.phan_tich_tai_chinh import bao_cao_tai_chinh, thong_ke_thang_tieu
from modules.du_bao_so_du import du_bao_so_du
from modules.phan_tich_pareto import analyze_pareto_by_category, analyze_pareto_by_month
from modules.truc_quan_du_lieu import visualize_data
from modules.insights_data_storytelling import generate_financial_insights


def main():
    """
    Hàm chính chạy toàn bộ pipeline phân tích tài chính cá nhân.
    """
    try:
        print("\n" + "="*50)
        print("💰 HỆ THỐNG PHÂN TÍCH TÀI CHÍNH CÁ NHÂN")
        print("="*50)

        # Bước 1: Đọc dữ liệu
        print("\n📂 Bước 1: Đọc dữ liệu...")
        df = doc_du_lieu("du_lieu/tai_chinh.csv")

        # Kiểm tra đọc file
        if df is None or df.empty:
            print("❌ Không đọc được dữ liệu.")
            return

        print(f"✅ Đã đọc {len(df)} giao dịch")

        # Bước 2: Làm sạch dữ liệu
        print("\n🧹 Bước 2: Làm sạch dữ liệu...")
        df = clean_data(df, remove_outliers=True)

        if df is None or df.empty:
            print("❌ Không có dữ liệu sau khi làm sạch")
            return

        print(f"✅ Dữ liệu sẵn sàng - {len(df)} giao dịch hợp lệ")

        # Bước 3: Phân loại chi tiêu
        print("\n🏷️  Bước 3: Phân loại chi tiêu tự động...")
        df = apply_auto_classification(df)
        print("✅ Đã phân loại xong")

        # Hiển thị mẫu
        print("\n📋 Mẫu dữ liệu (5 dòng đầu):")
        print(df.head())

        # Lưu kết quả vào file mới
        output_path = "du_lieu/tai_chinh_clean.csv"
        df.to_csv(output_path, index=False)
        print(f"\n✅ Đã lưu dữ liệu làm sạch: {output_path}")

        # Bước 4: Phân tích tài chính
        print("\n📊 Bước 4: Phân tích tài chính...")
        bao_cao_tai_chinh(df)

        # Bước 5: Dự báo số dư
        print("\n📈 Bước 5: Dự báo số dư 12 tháng...")
        forecast = du_bao_so_du(df)

        if not forecast.empty:
            print("\n✅ Kết quả dự báo (top 3):")
            print(forecast.head(3))
            
            # Lưu dự báo
            forecast.to_csv("du_lieu/du_bao_so_du.csv", index=False)
            print(f"\n✅ Đã lưu dự báo: du_lieu/du_bao_so_du.csv")
        else:
            print("⚠️  Không thể dự báo (dữ liệu không đủ)")

        # Bước 6: Trực quan hóa dữ liệu
        print("\n📊 Bước 6: Trực quan hóa dữ liệu...")
        visualize_data(df)

        # Bước 7: Phân tích insights và data storytelling
        print("\n🧠 Bước 7: Tạo insights và data storytelling...")
        generate_financial_insights(df)

        print("\n" + "="*50)
        print("✅ HOÀN THÀNH PHÂN TÍCH TÀI CHÍNH")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n⚠️  Chương trình bị dừng bởi người dùng")
    except Exception as exc:
        print(f"\n❌ Lỗi trong quá trình thực thi: {exc}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    




   
