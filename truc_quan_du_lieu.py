import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Thiết lập style cho biểu đồ
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 12
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["xtick.labelsize"] = 11
plt.rcParams["ytick.labelsize"] = 11


def _prepare_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa cột ngày tháng.

    Args:
        df (pd.DataFrame): DataFrame chứa cột 'date'.

    Returns:
        pd.DataFrame: DataFrame với cột 'date' đã chuẩn hóa.
    """
    try:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        return df
    except Exception as exc:
        print(f"❌ Lỗi chuẩn hóa ngày: {exc}")
        return df


def plot_monthly_cashflow(df: pd.DataFrame) -> None:
    """
    Vẽ biểu đồ dòng tiền theo tháng với insights.

    Args:
        df (pd.DataFrame): DataFrame chứa 'date' và 'amount'.
    """

    try:
        df = _prepare_date(df)

        if df.empty:
            print("⚠️  Không có dữ liệu để vẽ biểu đồ dòng tiền")
            return

        df["year_month"] = df["date"].dt.to_period("M")

        monthly_flow = (
            df.groupby("year_month")["amount"]
            .sum()
            .reset_index()
        )

        monthly_flow["year_month"] = monthly_flow["year_month"].astype(str)

        # Tính insights
        avg_flow = monthly_flow["amount"].mean()
        max_flow = monthly_flow["amount"].max()
        min_flow = monthly_flow["amount"].min()
        trend = "tăng" if monthly_flow["amount"].iloc[-1] > monthly_flow["amount"].iloc[0] else "giảm"

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(14, 8))

        bars = ax.bar(
            monthly_flow["year_month"],
            monthly_flow["amount"],
            color=['#e74c3c' if x < 0 else '#27ae60' for x in monthly_flow["amount"]],
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5
        )

        # Thêm đường trung bình
        ax.axhline(y=avg_flow, color='#f39c12', linestyle='--', linewidth=2,
                  label=f'Trung bình: {avg_flow:,.0f} VND')

        # Thêm giá trị trên mỗi bar
        for bar, value in zip(bars, monthly_flow["amount"]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (5 if height >= 0 else -15),
                   f'{value:,.0f}', ha='center', va='bottom' if height >= 0 else 'top',
                   fontsize=10, fontweight='bold')

        ax.set_title("Dòng tiền ròng theo tháng", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Tháng", fontsize=14)
        ax.set_ylabel("Dòng tiền (VND)", fontsize=14)
        ax.legend(loc='upper right')

        # Xoay nhãn x
        plt.xticks(rotation=45, ha='right')

        # Thêm insights text
        insight_text = f"""
        📊 Insights:
        • Trung bình: {avg_flow:,.0f} VND/tháng
        • Cao nhất: {max_flow:,.0f} VND
        • Thấp nhất: {min_flow:,.0f} VND
        • Xu hướng: {trend} dần
        """
        fig.text(0.02, 0.98, insight_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.tight_layout()
        plt.savefig("bao_cao/dong_tien_theo_thang.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Lưu biểu đồ: dong_tien_theo_thang.png")

    except Exception as exc:
        print(f"❌ Lỗi vẽ biểu đồ dòng tiền: {exc}")


def plot_category_spending(df: pd.DataFrame) -> None:
    """
    Vẽ biểu đồ chi tiêu theo danh mục với Pareto analysis.

    Args:
        df (pd.DataFrame): DataFrame chứa 'auto_category' và 'amount'.
    """

    try:
        df = df.copy()

        if df.empty:
            print("⚠️  Không có dữ liệu để vẽ biểu đồ chi tiêu")
            return

        spending = df[df["amount"] < 0].copy()

        if spending.empty:
            print("⚠️  Không có chi tiêu nào trong dữ liệu")
            return

        spending["amount"] = spending["amount"].abs()

        category_spend = (
            spending.groupby("auto_category")["amount"]
            .sum()
            .reset_index()
            .sort_values("amount", ascending=False)
        )

        # Tính Pareto
        total_spending = category_spend["amount"].sum()
        category_spend["percentage"] = category_spend["amount"] / total_spending * 100
        category_spend["cumulative"] = category_spend["percentage"].cumsum()

        # Vẽ biểu đồ
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Bar chart
        bars = ax1.bar(
            category_spend["auto_category"],
            category_spend["amount"],
            color=sns.color_palette("Set2", len(category_spend)),
            alpha=0.8,
            edgecolor='black',
            linewidth=0.5
        )

        # Pareto line
        ax2.plot(category_spend["auto_category"], category_spend["cumulative"],
                color='#e74c3c', marker='o', linewidth=3, markersize=8)
        ax2.axhline(y=80, color='#f39c12', linestyle='--', linewidth=2,
                   label='80% Pareto Line')

        # Styling
        ax1.set_title("Chi tiêu theo danh mục", fontsize=16, fontweight='bold')
        ax1.set_xlabel("Danh mục", fontsize=14)
        ax1.set_ylabel("Chi tiêu (VND)", fontsize=14)
        ax1.tick_params(axis='x', rotation=45)

        ax2.set_title("Pareto Analysis (80/20 Rule)", fontsize=16, fontweight='bold')
        ax2.set_xlabel("Danh mục", fontsize=14)
        ax2.set_ylabel("Tích lũy %", fontsize=14)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)

        # Thêm giá trị trên bar
        for bar, value, pct in zip(bars, category_spend["amount"], category_spend["percentage"]):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{value:,.0f}\n({pct:.1f}%)', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

        # Pareto insights
        pareto_items = category_spend[category_spend["cumulative"] <= 80]
        insight_text = f"""
        🎯 Pareto Insights:
        • {len(pareto_items)}/{len(category_spend)} danh mục
        • Chiếm 80% chi tiêu
        • Top: {pareto_items.iloc[0]['auto_category']}
        """
        fig.text(0.02, 0.98, insight_text, transform=ax1.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        plt.tight_layout()
        plt.savefig("bao_cao/chi_tieu_theo_danh_muc.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Lưu biểu đồ: chi_tieu_theo_danh_muc.png")

    except Exception as exc:
        print(f"❌ Lỗi vẽ biểu đồ chi tiêu: {exc}")


def plot_amount_vs_date_scatter(df: pd.DataFrame) -> None:
    """
    Vẽ biểu đồ phân tán giao dịch với density.

    Args:
        df (pd.DataFrame): DataFrame chứa 'date' và 'amount'.
    """

    try:
        df = _prepare_date(df)

        if df.empty:
            print("⚠️  Không có dữ liệu để vẽ biểu đồ phân tán")
            return

        df["day"] = df["date"].dt.day
        df["month"] = df["date"].dt.month

        # Tạo màu dựa trên tháng
        colors = plt.cm.Set3(np.linspace(0, 1, 12))

        fig, ax = plt.subplots(figsize=(14, 8))

        # Scatter plot với màu theo tháng
        scatter = ax.scatter(
            df["day"],
            df["amount"],
            c=df["month"],
            cmap='Set3',
            alpha=0.7,
            s=80,
            edgecolor='black',
            linewidth=0.5
        )

        # Thêm đường trung bình động
        df_sorted = df.sort_values('day')
        rolling_avg = df_sorted.groupby('day')['amount'].mean()
        ax.plot(rolling_avg.index, rolling_avg.values, color='#e74c3c',
               linewidth=3, alpha=0.8, label='Xu hướng trung bình')

        # Đường zero
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)

        ax.set_title("Phân bố giao dịch theo ngày trong tháng", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Ngày trong tháng", fontsize=14)
        ax.set_ylabel("Số tiền (VND)", fontsize=14)
        ax.legend(loc='upper right')

        # Colorbar cho tháng
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
        cbar.set_label('Tháng', fontsize=12)
        cbar.set_ticks(range(1, 13))
        cbar.set_ticklabels(['T1', 'T2', 'T3', 'T4', 'T5', 'T6',
                           'T7', 'T8', 'T9', 'T10', 'T11', 'T12'])

        # Insights
        income_count = len(df[df['amount'] > 0])
        expense_count = len(df[df['amount'] < 0])
        insight_text = f"""
        📈 Transaction Insights:
        • Tổng giao dịch: {len(df)}
        • Thu nhập: {income_count}
        • Chi tiêu: {expense_count}
        • Tỷ lệ: {expense_count/len(df)*100:.1f}%
        """
        fig.text(0.02, 0.98, insight_text, transform=ax.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

        plt.tight_layout()
        plt.savefig("bao_cao/phan_bo_giao_dich.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Lưu biểu đồ: phan_bo_giao_dich.png")

    except Exception as exc:
        print(f"❌ Lỗi vẽ biểu đồ phân tán: {exc}")


def plot_heatmap_category_month(df: pd.DataFrame) -> None:
    """
    Vẽ Heatmap chi tiêu theo danh mục và tháng với annotations.

    Args:
        df (pd.DataFrame): DataFrame chứa 'date', 'auto_category', 'amount'.
    """

    try:
        df = _prepare_date(df)

        if df.empty:
            print("⚠️  Không có dữ liệu để vẽ heatmap")
            return

        spending = df[df["amount"] < 0].copy()

        if spending.empty:
            print("⚠️  Không có chi tiêu nào để tạo heatmap")
            return

        spending["amount"] = spending["amount"].abs()
        spending["month"] = spending["date"].dt.month
        spending["month_name"] = spending["date"].dt.strftime('%b')

        pivot = spending.pivot_table(
            values="amount",
            index="auto_category",
            columns="month",
            aggfunc="sum",
            fill_value=0
        )

        # Tính phần trăm cho mỗi ô
        pivot_pct = pivot.div(pivot.sum().sum()) * 100

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        # Heatmap giá trị tuyệt đối
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".0f",
            cmap="YlOrRd",
            cbar_kws={'label': 'Chi tiêu (VND)', 'shrink': 0.8},
            ax=ax1,
            linewidths=0.5,
            square=True
        )

        ax1.set_title("Chi tiêu theo danh mục và tháng (VND)", fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel("Tháng", fontsize=14)
        ax1.set_ylabel("Danh mục", fontsize=14)

        # Heatmap phần trăm
        sns.heatmap(
            pivot_pct,
            annot=True,
            fmt=".1f",
            cmap="Blues",
            cbar_kws={'label': 'Phần trăm (%)', 'shrink': 0.8},
            ax=ax2,
            linewidths=0.5,
            square=True
        )

        ax2.set_title("Chi tiêu theo danh mục và tháng (%)", fontsize=16, fontweight='bold', pad=20)
        ax2.set_xlabel("Tháng", fontsize=14)
        ax2.set_ylabel("Danh mục", fontsize=14)

        # Insights
        max_value = pivot.max().max()
        max_category = pivot.max(axis=1).idxmax()
        max_month = pivot.loc[max_category].idxmax()

        insight_text = f"""
        🔥 Heatmap Insights:
        • Chi tiêu cao nhất: {max_value:,.0f} VND
        • Danh mục: {max_category}
        • Tháng: {max_month}
        • {pivot.sum().sum():,.0f} VND tổng chi tiêu
        """
        fig.text(0.02, 0.98, insight_text, transform=ax1.transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.9))

        plt.tight_layout()
        plt.savefig("bao_cao/heatmap_chi_tieu.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Lưu biểu đồ: heatmap_chi_tieu.png")

    except Exception as exc:
        print(f"❌ Lỗi vẽ heatmap: {exc}")


def plot_trend_analysis(df: pd.DataFrame) -> None:
    """
    Vẽ biểu đồ phân tích xu hướng chi tiêu.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch.
    """

    try:
        df = _prepare_date(df)

        if df.empty:
            print("⚠️  Không có dữ liệu để phân tích xu hướng")
            return

        # Tính xu hướng theo tháng
        monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
        monthly['date'] = monthly['date'].astype(str)

        # Tính đường trend
        x = np.arange(len(monthly))
        slope, intercept = np.polyfit(x, monthly['amount'].values, 1)
        trend_line = slope * x + intercept

        fig, ax = plt.subplots(figsize=(14, 8))

        # Vẽ dữ liệu thực tế
        ax.plot(monthly['date'], monthly['amount'], marker='o', linewidth=3,
               color='#3498db', markersize=8, label='Dữ liệu thực tế')

        # Vẽ đường trend
        ax.plot(monthly['date'], trend_line, '--', linewidth=3, color='#e74c3c',
               label=f'Xu hướng ({slope:.0f} VND/tháng)')

        # Điền vùng giữa
        ax.fill_between(monthly['date'], monthly['amount'], trend_line,
                       where=(monthly['amount'] > trend_line),
                       color='red', alpha=0.3, label='Trên xu hướng')
        ax.fill_between(monthly['date'], monthly['amount'], trend_line,
                       where=(monthly['amount'] <= trend_line),
                       color='green', alpha=0.3, label='Dưới xu hướng')

        ax.set_title("Phân tích xu hướng chi tiêu theo tháng", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Tháng", fontsize=14)
        ax.set_ylabel("Dòng tiền (VND)", fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha='right')

        # Insights
        trend_direction = "tăng" if slope > 0 else "giảm"
        insight_text = f"""
        📈 Trend Analysis:
        • Slope: {slope:,.0f} VND/tháng
        • Direction: {trend_direction}
        • R²: {np.corrcoef(x, monthly['amount'].values)[0,1]**2:.3f}
        • Reliability: {'Cao' if abs(slope) > 100 else 'Thấp'}
        """
        fig.text(0.02, 0.98, insight_text, transform=ax.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

        plt.tight_layout()
        plt.savefig("bao_cao/xu_huong_chi_tieu.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Lưu biểu đồ: xu_huong_chi_tieu.png")

    except Exception as exc:
        print(f"❌ Lỗi vẽ biểu đồ xu hướng: {exc}")


def visualize_data(df: pd.DataFrame) -> None:
    """
    Hàm tổng hợp trực quan hóa dữ liệu với tất cả biểu đồ.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu giao dịch.
    """

    try:
        if df is None or df.empty:
            print("⚠️  Không có dữ liệu để vẽ biểu đồ")
            return

        print("\n🎨 Bắt đầu trực quan hóa dữ liệu...")

        plot_monthly_cashflow(df)
        plot_category_spending(df)
        plot_amount_vs_date_scatter(df)
        plot_heatmap_category_month(df)
        plot_trend_analysis(df)

        print("\n✅ Hoàn thành trực quan hóa dữ liệu - 5 biểu đồ đã tạo")

    except Exception as exc:
        print(f"❌ Lỗi trực quan hóa: {exc}")