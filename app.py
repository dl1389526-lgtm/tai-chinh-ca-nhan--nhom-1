"""
🎨 Streamlit Web App - Personal Financial Analysis Dashboard
Giao diện web tương tác cho hệ thống phân tích tài chính cá nhân
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from pathlib import Path
import sys

# ✅ Import modules AI
try:
    from modules.insights_data_storytelling import (
        generate_financial_insights,
        print_insights,
        create_data_story
    )
    from modules.phan_tich_pareto import (
        analyze_pareto_by_category,
        analyze_pareto_by_month
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="💰 Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# CSS STYLING
# ======================

st.markdown("""
<style>

.main {
    background: linear-gradient(135deg, #f5f7fb 0%, #c3cfe2 100%);
    padding: 2rem;
}

h1, h2, h3 {
    color: #0066cc;
    font-weight: bold;
}

/* Card styling */
[data-testid="metric-container"] {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border-left: 5px solid #0066cc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* Buttons */
.stButton > button {
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s;
}

.stButton > button:hover {
    background-color: #0052a3;
    box-shadow: 0 5px 15px rgba(0,102,204,0.3);
}

</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================

@st.cache_data(ttl=10)
def load_data():
    """Load financial data từ CSV files"""
    file_paths = [
        Path("du_lieu/tai_chinh_clean.csv"),
        Path("du_lieu/tai_chinh.csv"),
        Path("tai_chinh.csv")
    ]
    
    for file_path in file_paths:
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                if len(df) > 0:
                    # Normalize column names (case-insensitive)
                    df.columns = df.columns.str.lower()
                    
                    # Rename columns to standard format
                    column_mapping = {
                        'date': 'date',
                        'amount': 'amount', 
                        'description': 'description',
                        'category': 'category',
                        'auto_category': 'auto_category'
                    }
                    
                    # Apply mapping for existing columns
                    for old_col, new_col in column_mapping.items():
                        if old_col in df.columns:
                            df = df.rename(columns={old_col: new_col})
                    
                    # Convert date column
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                    df = df.dropna(subset=["date"])
                    
                    return df, str(file_path)
            except Exception as e:
                st.warning(f"⚠️ Lỗi đọc file {file_path}: {e}")
    
    # Return empty dataframe if no file found
    return pd.DataFrame(columns=["date", "amount", "description"]), "N/A"

df, data_file = load_data()

# Add month column for grouping
if len(df) > 0 and "date" in df.columns:
    df["month"] = df["date"].dt.to_period("M")
    df["category"] = df["auto_category"] if "auto_category" in df.columns else "Chưa phân loại"

# ======================
# SIDEBAR MENU
# ======================

with st.sidebar:
    st.title("📂 Menu Navigation")
    st.divider()
    
    menu = st.radio(
        "Chọn trang",
        [
            "📊 Dashboard",
            "� Nhập Dữ Liệu",
            "�💡 AI Insights",
            "📈 Phân Tích",
            "📉 Dự Báo",
            "📋 Lịch Sử"
        ],
        key="menu"
    )
    
    st.divider()
    st.caption(f"📁 Dữ liệu: {data_file}")
    st.caption(f"📝 Giao dịch: {len(df)}")
    
    if len(df) > 0:
        date_range = f"{df['date'].min().date()} → {df['date'].max().date()}"
        st.caption(f"📅 Khoảng thời gian: {date_range}")

# ======================
# MAIN DASHBOARD
# ======================

if menu == "📊 Dashboard":
    st.title("💰 Dashboard Tài Chính Cá Nhân")
    st.divider()
    
    if len(df) > 0:
        # Calculate metrics
        income = df[df["amount"] > 0]["amount"].sum()
        expense = abs(df[df["amount"] < 0]["amount"].sum())
        balance = income - expense
        savings_rate = (balance / income * 100) if income > 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💵 Thu Nhập",
                f"{income:,.0f} VND",
                delta="Tổng cộng"
            )
        
        with col2:
            st.metric(
                "💸 Chi Tiêu",
                f"{expense:,.0f} VND",
                delta=-expense
            )
        
        with col3:
            st.metric(
                "⚖️ Số Dư",
                f"{balance:,.0f} VND",
                delta=f"{savings_rate:.1f}%"
            )
        
        with col4:
            st.metric(
                "📊 Tỷ Lệ Tiết Kiệm",
                f"{savings_rate:.1f}%",
                delta="Mục tiêu: 20%"
            )
        
        st.divider()
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("💳 Chi Tiêu Theo Danh Mục")
            
            expense_data = df[df["amount"] < 0].copy()
            expense_data["amount"] = expense_data["amount"].abs()
            expense_by_category = expense_data.groupby("category")["amount"].sum().sort_values(ascending=False)
            
            if len(expense_by_category) > 0:
                fig_pie = px.pie(
                    values=expense_by_category.values,
                    names=expense_by_category.index,
                    title="Phân bố chi tiêu",
                    hole=0.3
                )
                st.plotly_chart(fig_pie, width='stretch')
            else:
                st.info("Chưa có dữ liệu chi tiêu")
        
        with chart_col2:
            st.subheader("📈 Xu Hướng Tài Chính Theo Tháng")
            
            if len(df) > 1:
                monthly = df.groupby("month")["amount"].sum()
                
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=[str(d) for d in monthly.index],
                    y=monthly.values,
                    mode='lines+markers',
                    name='Số dư',
                    line=dict(color='#0066cc', width=3),
                    marker=dict(size=8)
                ))
                
                st.plotly_chart(fig_line, width='stretch')
            else:
                st.info("Chưa đủ dữ liệu để hiển thị biểu đồ")
        
        st.divider()
        
        # Summary stats
        st.subheader("📊 Thống Kê Cơ Bản")
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            avg_transaction = df["amount"].abs().mean()
            st.metric("📌 Giao dịch trung bình", f"{avg_transaction:,.0f} VND")
        
        with stat_col2:
            max_expense = abs(df[df["amount"] < 0]["amount"].max()) if len(df[df["amount"] < 0]) > 0 else 0
            st.metric("📍 Chi tiêu lớn nhất", f"{max_expense:,.0f} VND")
        
        with stat_col3:
            total_transactions = len(df)
            st.metric("📊 Tổng giao dịch", f"{total_transactions}")
    
    else:
        st.warning("⚠️ Không có dữ liệu. Hãy thêm giao dịch hoặc kiểm tra file dữ liệu.")

# ======================
# DATA INPUT
# ======================

elif menu == "📥 Nhập Dữ Liệu":
    st.title("📥 Nhập Dữ Liệu Giao Dịch")
    st.divider()
    
    # Two columns for upload and manual input
    col_upload, col_manual = st.tabs(["📂 Tải File CSV", "✍️ Nhập Thủ Công"])
    
    with col_upload:
        st.subheader("📂 Tải Lên File CSV")
        st.markdown("""
        **Format file CSV yêu cầu:**
        - Cột `date`: Ngày giao dịch (DD/MM/YYYY hoặc YYYY-MM-DD)
        - Cột `amount`: Số tiền (dương = thu, âm = chi)
        - Cột `description`: Mô tả giao dịch
        - Optional: `category` hoặc `auto_category`
        """)
        
        uploaded_file = st.file_uploader("Chọn file CSV", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Read uploaded file
                uploaded_df = pd.read_csv(uploaded_file)
                
                st.success(f"✅ Đã tải {len(uploaded_df)} giao dịch")
                
                # Show preview
                st.subheader("👁️ Xem Trước")
                st.dataframe(uploaded_df.head(), width='stretch')
                
                # Validate columns
                required_cols = ['date', 'amount']
                missing_cols = [col for col in required_cols if col not in uploaded_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Thiếu cột: {', '.join(missing_cols)}")
                else:
                    # Save button
                    if st.button("💾 Lưu Dữ Liệu", key="save_upload"):
                        # Create backup
                        import shutil
                        backup_path = "du_lieu/tai_chinh_backup.csv"
                        if Path("du_lieu/tai_chinh.csv").exists():
                            shutil.copy("du_lieu/tai_chinh.csv", backup_path)
                        
                        # Save new data
                        Path("du_lieu").mkdir(exist_ok=True)
                        uploaded_df.to_csv("du_lieu/tai_chinh.csv", index=False)
                        
                        st.success("✅ Dữ liệu đã được lưu!")
                        st.info("🔄 Tải lại trang để xem dữ liệu mới")
                        
                st.divider()
                st.subheader("📊 Thống Kê File")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📝 Số giao dịch", len(uploaded_df))
                
                with col2:
                    total_amount = uploaded_df['amount'].sum()
                    st.metric("💰 Tổng", f"{total_amount:,.0f} VND")
                
                with col3:
                    if 'date' in uploaded_df.columns:
                        date_cols = pd.to_datetime(uploaded_df['date'], errors='coerce')
                        valid_dates = date_cols.dropna()
                        if len(valid_dates) > 0:
                            date_range = f"{valid_dates.min().date()} → {valid_dates.max().date()}"
                            st.metric("📅 Khoảng thời gian", date_range)
                
            except Exception as e:
                st.error(f"❌ Lỗi đọc file: {e}")
        
        else:
            # Show sample file format
            st.subheader("📋 Ví Dụ Định Dạng")
            
            sample_data = {
                "date": ["2024-01-01", "2024-01-02", "2024-01-05"],
                "amount": [5000000, -200000, -150000],
                "description": ["Lương tháng 1", "Ăn uống", "Xăng xe"],
                "category": ["Lương", "Ăn uống", "Đi lại"]
            }
            sample_df = pd.DataFrame(sample_data)
            
            st.info("💡 Tệp CSV của bạn nên có định dạng như sau:")
            st.dataframe(sample_df, width='stretch')
            
            # Download sample
            csv_sample = sample_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Tải Mẫu CSV",
                data=csv_sample,
                file_name="sample_tai_chinh.csv",
                mime="text/csv",
                key="sample_csv"
            )
    
    with col_manual:
        st.subheader("✍️ Nhập Giao Dịch Thủ Công")
        
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                trans_date = st.date_input("📅 Ngày", key="trans_date")
                trans_amount = st.number_input("💰 Số tiền (VND)", min_value=-1000000000, max_value=1000000000, key="trans_amount")
            
            with col2:
                trans_type = st.selectbox("📌 Loại", ["Chi tiêu", "Thu nhập"], key="trans_type")
                trans_category = st.selectbox(
                    "🏷️ Danh mục",
                    ["Ăn uống", "Mua sắm", "Đi lại", "Giáo dục", "Sức khỏe", 
                     "Tiện ích", "Giải trí", "Khác", "Lương"],
                    key="trans_category"
                )
            
            trans_description = st.text_input("📝 Mô tả", key="trans_description")
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("➕ Thêm Giao Dịch", use_container_width=True)
            
            with col2:
                st.form_submit_button("❌ Hủy", use_container_width=True)
        
        if submitted:
            try:
                # Adjust amount based on type
                final_amount = trans_amount if trans_type == "Thu nhập" else -abs(trans_amount)
                
                # Load existing data
                if Path("du_lieu/tai_chinh.csv").exists():
                    new_df = pd.read_csv("du_lieu/tai_chinh.csv")
                else:
                    new_df = pd.DataFrame(columns=["date", "amount", "description", "category"])
                
                # Add new transaction
                new_row = pd.DataFrame({
                    "date": [trans_date],
                    "amount": [final_amount],
                    "description": [trans_description],
                    "category": [trans_category]
                })
                
                new_df = pd.concat([new_df, new_row], ignore_index=True)
                
                # Save
                Path("du_lieu").mkdir(exist_ok=True)
                new_df.to_csv("du_lieu/tai_chinh.csv", index=False)
                
                st.success("✅ Giao dịch đã được thêm!")
                st.balloons()
                st.info("🔄 Tải lại trang để xem dữ liệu mới")
                
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
        
        st.divider()
        
        # Recent transactions
        if Path("du_lieu/tai_chinh.csv").exists():
            st.subheader("📋 Giao Dịch Gần Đây")
            
            recent_df = pd.read_csv("du_lieu/tai_chinh.csv").tail(5)
            st.dataframe(recent_df, width='stretch')

# ======================
# AI INSIGHTS
# ======================

elif menu == "💡 AI Insights":
    st.title("🤖 AI Insights & Phân Tích Thông Minh")
    st.divider()
    
    if not AI_AVAILABLE:
        st.error("❌ Modules AI không được cài đặt. Hãy kiểm tra requirements.txt")
    elif len(df) < 5:
        st.warning("⚠️ Cần ít nhất 5 giao dịch để tạo insights")
    else:
        try:
            # Generate AI insights
            insights = generate_financial_insights(df)
            
            # Display insights in tabs
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "Tổng Quan",
                "Chi Tiêu",
                "Xu Hướng",
                "Pareto",
                "Khuyến Nghị",
                "Rủi Ro",
                "Sức Khỏe"
            ])
            
            with tab1:
                if "overview" in insights:
                    st.markdown(insights["overview"])
            
            with tab2:
                if "spending_patterns" in insights:
                    st.markdown(insights["spending_patterns"])
            
            with tab3:
                if "trends" in insights:
                    st.markdown(insights["trends"])
            
            with tab4:
                if "pareto" in insights:
                    st.markdown(insights["pareto"])
            
            with tab5:
                if "recommendations" in insights:
                    st.markdown(insights["recommendations"])
            
            with tab6:
                if "risk_assessment" in insights:
                    st.markdown(insights["risk_assessment"])
            
            with tab7:
                if "financial_health" in insights:
                    st.markdown(insights["financial_health"])
            
            # Data story
            st.divider()
            st.subheader("📖 Câu Chuyện Tài Chính Của Bạn")
            
            if st.button("🎯 Tạo câu chuyện dữ liệu"):
                with st.spinner("Đang tạo câu chuyện..."):
                    story = create_data_story(df)
                    st.markdown(story)
        
        except Exception as e:
            st.error(f"❌ Lỗi tạo insights: {e}")

# ======================
# ANALYSIS
# ======================

elif menu == "📈 Phân Tích":
    st.title("📈 Phân Tích Chuyên Sâu")
    st.divider()
    
    if len(df) < 3:
        st.warning("⚠️ Cần ít nhất 3 giao dịch để phân tích")
    else:
        analysis_tab1, analysis_tab2 = st.tabs(["Pareto Analysis", "Distribution"])
        
        with analysis_tab1:
            st.subheader("🎯 Phân Tích Pareto (20/80 Rule)")
            
            expense_data = df[df["amount"] < 0].copy()
            expense_data["amount"] = expense_data["amount"].abs()
            
            if len(expense_data) > 0:
                cat_total = expense_data.groupby("category")["amount"].sum().sort_values(ascending=False)
                cat_cumsum = cat_total.cumsum()
                cat_pct = (cat_cumsum / cat_total.sum() * 100).head()
                
                fig_pareto = go.Figure()
                fig_pareto.add_trace(go.Bar(
                    x=cat_pct.index,
                    y=cat_pct.values,
                    name="Tích lũy %"
                ))
                
                st.plotly_chart(fig_pareto, width='stretch')
                
                st.info(f"💡 {len(cat_pct)} danh mục hàng đầu chiếm {cat_pct.iloc[-1]:.1f}% chi tiêu")
        
        with analysis_tab2:
            st.subheader("📊 Phân Bố Chi Tiêu")
            
            expense_data = df[df["amount"] < 0].copy()
            expense_data["amount"] = -expense_data["amount"]
            
            fig_hist = px.histogram(
                expense_data,
                x="amount",
                nbins=30,
                title="Phân bố amount giao dịch"
            )
            
            st.plotly_chart(fig_hist, width='stretch')

# ======================
# FORECASTING
# ======================

elif menu == "📉 Dự Báo":
    st.title("📉 Dự Báo Tài Chính 12 Tháng")
    st.divider()
    
    if len(df) < 3:
        st.warning("⚠️ Cần ít nhất 3 tháng dữ liệu để dự báo")
    else:
        try:
            expense_data = df[df["amount"] < 0].copy()
            
            if len(expense_data) > 0:
                monthly = expense_data.groupby(expense_data["date"].dt.to_period("M"))["amount"].sum()
                
                if len(monthly) >= 2:
                    y = monthly.values
                    X = np.arange(len(y)).reshape(-1, 1)
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Forecast 12 months
                    future = np.arange(len(y), len(y) + 12).reshape(-1, 1)
                    prediction = model.predict(future)
                    
                    # Combine historical and forecast
                    all_values = np.concatenate([y, prediction])
                    all_months = np.arange(len(all_values))
                    
                    # Create figure
                    fig_forecast = go.Figure()
                    
                    # Historical data
                    fig_forecast.add_trace(go.Scatter(
                        x=all_months[:len(y)],
                        y=y,
                        mode='lines+markers',
                        name='Chi tiêu thực tế',
                        line=dict(color='#0066cc', width=3)
                    ))
                    
                    # Forecast
                    fig_forecast.add_trace(go.Scatter(
                        x=all_months[len(y)-1:],
                        y=np.concatenate([[y[-1]], prediction]),
                        mode='lines+markers',
                        name='Dự báo',
                        line=dict(color='#ff6600', width=3, dash='dash')
                    ))
                    
                    fig_forecast.update_layout(
                        title="Dự báo chi tiêu 12 tháng",
                        xaxis_title="Tháng",
                        yaxis_title="Chi tiêu (VND)",
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    # Statistics
                    st.subheader("📊 Thống Kê Dự Báo")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_historical = y.mean()
                        st.metric("Trung bình thực tế", f"{abs(avg_historical):,.0f} VND")
                    
                    with col2:
                        avg_forecast = prediction.mean()
                        st.metric("Trung bình dự báo", f"{abs(avg_forecast):,.0f} VND")
                    
                    with col3:
                        change_pct = ((avg_forecast - avg_historical) / avg_historical * 100) if avg_historical != 0 else 0
                        st.metric("Thay đổi", f"{change_pct:.1f}%")
                else:
                    st.info("Chưa đủ dữ liệu để dự báo")
            else:
                st.warning("⚠️ Không có dữ liệu chi tiêu")
        
        except Exception as e:
            st.error(f"❌ Lỗi dự báo: {e}")

# ======================
# TRANSACTION HISTORY
# ======================

elif menu == "📋 Lịch Sử":
    st.title("📋 Lịch Sử Giao Dịch")
    st.divider()
    
    if len(df) == 0:
        st.info("📁 Không có giao dịch nào")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Loại giao dịch",
                ["Tất cả", "Thu nhập", "Chi tiêu"],
                key="filter_type"
            )
        
        with col2:
            categories = df["category"].unique().tolist()
            selected_category = st.multiselect(
                "Danh mục",
                categories,
                default=categories[:3] if len(categories) > 3 else categories,
                key="filter_category"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sắp xếp",
                ["Ngày (mới nhất)", "Ngày (cũ nhất)", "Số tiền (cao)"],
                key="sort_by"
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if filter_type == "Thu nhập":
            filtered_df = filtered_df[filtered_df["amount"] > 0]
        elif filter_type == "Chi tiêu":
            filtered_df = filtered_df[filtered_df["amount"] < 0]
        
        if selected_category:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_category)]
        
        # Sort
        if sort_by == "Ngày (mới nhất)":
            filtered_df = filtered_df.sort_values("date", ascending=False)
        elif sort_by == "Ngày (cũ nhất)":
            filtered_df = filtered_df.sort_values("date", ascending=True)
        else:
            filtered_df = filtered_df.sort_values("amount", key=abs, ascending=False)
        
        # Display
        st.subheader(f"📝 {len(filtered_df)} giao dịch")
        
        # Format for display
        display_df = filtered_df[["date", "description", "amount", "category"]].copy()
        display_df["amount"] = display_df["amount"].apply(lambda x: f"{x:,.0f} VND")
        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")
        
        st.dataframe(
            display_df.rename(columns={
                "date": "📅 Ngày",
                "description": "📝 Mô Tả",
                "amount": "💰 Số Tiền",
                "category": "🏷️ Danh Mục"
            }),
            width='stretch',
            height=600
        )
        
        # Export
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            # Create dynamic filename based on filters
            filename_parts = ["giao_dich"]
            if filter_type != "Tất cả":
                filename_parts.append(filter_type.lower().replace(" ", "_"))
            if selected_category:
                if len(selected_category) == 1:
                    filename_parts.append(selected_category[0].lower().replace(" ", "_"))
                else:
                    filename_parts.append("nhieu_danh_muc")
            filename_parts.append(datetime.now().strftime('%Y%m%d'))

            dynamic_filename = "_".join(filename_parts) + ".csv"

            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Tải CSV Đã Lọc",
                data=csv,
                file_name=dynamic_filename,
                mime="text/csv",
                help=f"Tải {len(filtered_df)} giao dịch đã lọc"
            )

        with col2:
            total_amount = filtered_df['amount'].sum()
            st.metric("💰 Tổng cộng", f"{total_amount:,.0f} VND")

# ======================
# FOOTER
# ======================

st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption("💡 Mẹo: Sử dụng menu bên trái để điều hướng")

with footer_col2:
    st.caption("🔄 Dữ liệu cập nhật tự động")

with footer_col3:
    st.caption(f"⏰ Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}")