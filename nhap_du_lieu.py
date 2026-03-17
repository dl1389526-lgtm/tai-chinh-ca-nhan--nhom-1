import os
import pandas as pd


def doc_du_lieu(duong_dan_file: str) -> pd.DataFrame | None:
    """
    Đọc dữ liệu từ file CSV.
    """

    if not os.path.exists(duong_dan_file):
        print("Không tìm thấy file:", duong_dan_file)
        return None

    try:
        df = pd.read_csv(duong_dan_file)
        print("Đọc dữ liệu thành công!")
        return df

    except pd.errors.ParserError:
        print("File CSV sai định dạng.")
        return None

    except Exception as exc:
        print("Lỗi khi đọc file:", exc)
        return None


def nhap_giao_dich() -> dict:
    """
    Nhập giao dịch mới từ bàn phím với validation.
    
    Returns:
        dict: Dictionary chứa thông tin giao dịch hoặc dict rỗng nếu lỗi.
    """

    try:
        print("\n--- Nhập Giao Dịch Mới ---")
        
        # Nhập và validate ngày
        while True:
            try:
                ngay = input("Ngày (YYYY-MM-DD) [hoặc Enter để bỏ qua]: ").strip()
                if not ngay:
                    ngay = pd.Timestamp.now().strftime("%Y-%m-%d")
                pd.to_datetime(ngay)
                break
            except ValueError:
                print("❌ Định dạng ngày không hợp lệ. Vui lòng nhập lại (YYYY-MM-DD)")
        
        mo_ta = input("Mô tả giao dịch: ").strip() or "N/A"
        
        # Validate số tiền
        while True:
            try:
                so_tien_input = input("Số tiền (VND): ").strip()
                so_tien = float(so_tien_input)
                if so_tien < 0:
                    print("❌ Số tiền phải >= 0")
                    continue
                break
            except ValueError:
                print("❌ Số tiền phải là số. Vui lòng nhập lại")
        
        # Validate loại giao dịch
        while True:
            loai = input("Loại giao dịch (credit/debit): ").strip().lower()
            if loai in ["credit", "debit"]:
                break
            print("❌ Loại phải là 'credit' hoặc 'debit'")
        
        danh_muc = input("Danh mục: ").strip() or "Other"
        
        return {
            "date": ngay,
            "description": mo_ta,
            "amount": so_tien,
            "transaction_type": loai,
            "category": danh_muc,
            "account_name": "Manual Entry",
        }
        
    except KeyboardInterrupt:
        print("\n⚠️  Nhập liệu bị hủy")
        return {}
    except Exception as exc:
        print(f"❌ Lỗi nhập dữ liệu: {exc}")
        return {}