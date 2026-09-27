import os
from datetime import datetime
import pandas as pd
import streamlit as st
st.image("logo1.jpg")
st.set_page_config(page_title="Order Nhà Hàng", layout="wide")

# Đường dẫn file dữ liệu dùng chung trên máy chủ
CSV_FILE = "history.csv"

# Thực đơn cố định của nhà hàng Mr. Bình
menu = {
    "Đồ ăn": {
        "Pizza Hải Sản": 150000,"Pizza cá": 500000,
        "Mì Ý Bò Bằm": 95000,"GÀ CHIÊN MẮM TỎI":29000,
        "Burger Gà": 35000,
        "Bít tết Bò Mỹ": 250000,
        "Sườn nướng BBQ": 150000,
        "Cánh gà chiên mắm": 75000,
        "Lẩu cá diêu hồng": 200000,
        "Lẩu Thái hải sản": 300000,
    },
    "Thức uống": {
        "Coca Cola": 20000,
        "Trà sữa SV": 70000,
        "Trà Đào Cam Sả": 35000,
        "Cà Phê Sữa": 25000,
        "Nước Suối": 10000,
        "Sinh tố Bơ": 45000,
        "Nước ép cam": 40000,
        "Mojito chanh dây": 55000,
        "Bia Heineken": 30000,
    },
}

if "order_dict" not in st.session_state:
    st.session_state.order_dict = {}

# Tự động tải dữ liệu lịch sử cũ từ file CSV lên hệ thống khi khởi động ứng dụng
if "history" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            # Đọc file CSV lưu trữ chung
            df_loaded = pd.read_csv(CSV_FILE)
            # Chuyển đổi ngược lại thành danh sách dict để duy trì tính nhất quán của code
            st.session_state.history = df_loaded.to_dict(orient="records")
        except Exception:
            st.session_state.history = []
    else:
        st.session_state.history = []

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Thanh điều hướng dạng RADIO hiển thị trực diện ngay trên Sidebar
page = st.sidebar.radio("📋 Chọn trang hệ thống", ["🍽️ Order", "🔑 Admin"])

if page == "🍽️ Order":
    st.title("🍽️ Hệ thống Order Nhà Hàng_Dr Bình")
    st.caption("Ghi nhận order nhanh chóng và chính xác theo thời gian thực")

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.subheader("Chọn Món")
        table_number = st.selectbox(
            "🪑 Chọn số bàn", [f"Bàn {i}" for i in range(1, 21)]
        )
        category = st.selectbox("Chọn loại:", list(menu.keys()))
        item = st.selectbox("Chọn món:", list(menu[category].keys()))
        quantity = st.number_input("Số lượng:", min_value=1, step=1, value=1)

        if st.button("Thêm vào giỏ"):
            price = menu[category][item]

            if item in st.session_state.order_dict:
                st.session_state.order_dict[item]["Số lượng"] += quantity
                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"] * price
                )
                st.session_state.order_dict[item]["Bàn"] = table_number
            else:
                st.session_state.order_dict[item] = {
"Bàn": table_number,
                    "Tên món": item,
                    "Đơn giá": price,
                    "Số lượng": quantity,
                    "Thành tiền": price * quantity,
                }
            st.success(f"Đã thêm {item} vào giỏ!")
            st.rerun()

    with col2:
        st.subheader("Giỏ hàng hiện tại")

        if st.session_state.order_dict:
            df = pd.DataFrame.from_dict(
                st.session_state.order_dict, orient="index"
            )
            st.table(
                df[["Bàn", "Tên món", "Đơn giá", "Số lượng", "Thành tiền"]]
            )

            tam_tinh = df["Thành tiền"].sum()
            # Giảm giá 5% cho hóa đơn trên 1 triệu đồng
            giam_gia = tam_tinh * 0.05 if tam_tinh > 1000000 else 0
            tong_thanh_toan = tam_tinh - giam_gia

            st.write(f"**Tạm tính:** {tam_tinh:,.0f} VNĐ")
            if giam_gia > 0:
                st.write(f"**Giảm giá (5% > 1M):** -{giam_gia:,.0f} VNĐ")
            st.metric("Tổng thanh toán thực tế", f"{tong_thanh_toan:,.0f} VNĐ")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("💳 Thanh toán"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Ghi nhận các món vào danh sách lịch sử
                    for row in st.session_state.order_dict.values():
                        st.session_state.history.append(
                            {
                                "Thời gian": now_str,
                                "Bàn": row["Bàn"],
                                "Tên món": row["Tên món"],
                                "Số lượng": row["Số lượng"],
                                "Thành tiền": row["Thành tiền"],
                            }
                        )

                    # ĐỒNG BỘ: Lưu dữ liệu mới xuống tệp tin CSV dùng chung
                    try:
                        df_history = pd.DataFrame(st.session_state.history)
                        df_history.to_csv(
                            CSV_FILE, index=False, encoding="utf-8-sig"
                        )
                    except Exception as e:
                        st.error(f"Lỗi ghi dữ liệu xuống máy chủ: {e}")

                    st.success(
                        "Thanh toán thành công! Dữ liệu đã được lưu trữ vĩnh viễn."
                    )
                    st.session_state.order_dict = {}
                    st.rerun()

            with col_btn2:
                if st.button("🗑️ Xóa toàn bộ giỏ"):
                    st.session_state.order_dict = {}
                    st.rerun()
        else:
            st.info(
                "Giỏ hàng đang trống. Hãy chọn món ăn/đồ uống bên trái để lên đơn."
            )
elif page == "🔑 Admin":
    st.title("🔑 Trang Quản Trị & Phân Tích Doanh Thu")

    if not st.session_state.admin_logged_in:
        with st.form("admin_login_form"):
            password = st.text_input("Nhập mật khẩu quản trị", type="password")
            login_submitted = st.form_submit_button("🔑 Đăng nhập")

            if login_submitted:
                if password == "123456":
                    st.session_state.admin_logged_in = True
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Mật khẩu không chính xác!")

        st.warning(
            "Vui lòng nhập mật khẩu và bấm đăng nhập để xem dữ liệu kinh doanh."
        )
        st.stop()

    col_header_title, col_header_btn = st.columns([4, 1])
    with col_header_title:
        st.success("Xác thực quyền Quản trị viên thành công!")
    with col_header_btn:
        if st.button("🔒 Đăng xuất"):
            st.session_state.admin_logged_in = False
            st.rerun()

    # Phân tách trang quản trị thành các tab rõ ràng
    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Danh sách thực đơn",
            "💰 Doanh thu & Nhật ký giao dịch",
            "📊 Thống kê & Phân tích bán hàng REAL-TIME",
        ]
    )

    # --- TAB 1: DANH SÁCH THỰC ĐƠN ---
    with tab1:
        st.subheader("Menu hiện hành của nhà hàng")
        data = []
        for category in menu:
            for item, price in menu[category].items():
                data.append([category, item, price])

        df_menu = pd.DataFrame(
            data, columns=["Phân loại", "Tên món", "Đơn giá (VNĐ)"]
        )
        st.dataframe(df_menu, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Doanh thu & Hóa đơn thực tế từ khách gọi")

        # Cập nhật đọc trực tiếp từ tệp tin CSV để đảm bảo chính xác đồng bộ
        if os.path.exists(CSV_FILE):
            try:
                df_history = pd.read_csv(CSV_FILE)
            except Exception:
                df_history = pd.DataFrame()
        else:
            df_history = pd.DataFrame()

        if not df_history.empty:
            tong_doanh_thu = df_history["Thành tiền"].sum()

            col_met1, col_met2 = st.columns(2)
            col_met1.metric(
                "Tổng doanh thu tích lũy (Real-time)", f"{tong_doanh_thu:,.0f} VNĐ"
            )
            col_met2.metric(
                "Số lượng món đã phục vụ", f"{df_history['Số lượng'].sum()} phần"
            )

            st.markdown("---")
            st.subheader("📅 Thống kê doanh thu theo Ngày")

            # Trích xuất ngày từ trường thời gian thật
            df_history["Ngày"] = pd.to_datetime(df_history["Thời gian"]).dt.date
            df_daily_revenue = (
df_history.groupby("Ngày")["Thành tiền"].sum().reset_index()
            )
            df_daily_revenue.columns = ["Ngày", "Doanh thu (VNĐ)"]

            col_chart_day, col_table_day = st.columns([1.5, 1])
            with col_chart_day:
                st.write("**Biểu đồ doanh thu hàng ngày:**")
                st.bar_chart(df_daily_revenue.set_index("Ngày")["Doanh thu (VNĐ)"])

            with col_table_day:
                st.write("**Bảng kê doanh thu theo ngày:**")
                st.dataframe(
                    df_daily_revenue.style.format(
                        {"Doanh thu (VNĐ)": "{:,.0f} VNĐ"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("---")
            st.subheader("Chi tiết lịch sử thanh toán thực tế")
            st.dataframe(
                df_history[["Thời gian", "Bàn", "Tên món", "Số lượng", "Thành tiền"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Hệ thống chưa ghi nhận bất kỳ giao dịch thanh toán nào từ khách hàng."
            )

    with tab3:
        st.subheader("📊 Phân tích số liệu và Khung giờ vàng")

        # Cập nhật đọc trực tiếp từ tệp tin CSV
        if os.path.exists(CSV_FILE):
            try:
                df_anal = pd.read_csv(CSV_FILE)
            except Exception:
                df_anal = pd.DataFrame()
        else:
            df_anal = pd.DataFrame()

        if not df_anal.empty:
            df_anal["Thời gian"] = pd.to_datetime(df_anal["Thời gian"])
            df_anal["Giờ"] = df_anal["Thời gian"].dt.hour
            df_anal["Tháng-Năm"] = df_anal["Thời gian"].dt.strftime("%m/%Y")

            # 1. Tìm các chỉ số vàng từ dữ liệu thực tế
            best_seller = df_anal.groupby("Tên món")["Số lượng"].sum().idxmax()
            best_seller_qty = df_anal.groupby("Tên món")["Số lượng"].sum().max()

            hourly_sales = df_anal.groupby("Giờ")["Số lượng"].sum()
            best_hour = hourly_sales.idxmax()
            best_hour_qty = hourly_sales.max()

            best_month = (
                df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().idxmax()
            )
            best_month_rev = (
                df_anal.groupby("Tháng-Năm")["Thành tiền"].sum().max()
            )

            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.info("🏆 MÓN BÁN CHẠY NHẤT")
                st.metric(label=best_seller, value=f"{best_seller_qty} phần")
            with col_kpi2:
                st.warning("⚡ KHUNG GIỜ VÀNG (Đông khách nhất)")
                st.metric(
                    label=f"Khung giờ: {best_hour:02d}:00 - {(best_hour+1):02d}:00",
value=f"{best_hour_qty} phần",
                )
            with col_kpi3:
                st.success("📅 THÁNG DOANH THU ĐỈNH ĐIỂM")
                st.metric(label=f"Tháng {best_month}", value=f"{best_month_rev:,.0f} VNĐ")

            st.markdown("---")

            # Phân tích chi tiết lượng bán/doanh thu từng món ăn
            st.write("### 🍔 Doanh thu & Số lượng tiêu thụ của từng món ăn")
            summary_mon = (
                df_anal.groupby("Tên món")
                .agg(
                    Số_lượng_bán=("Số lượng", "sum"),
                    Doanh_thu=("Thành tiền", "sum"),
                )
                .reset_index()
            )
            summary_mon = summary_mon.sort_values(
                by="Số_lượng_bán", ascending=False
            )

            col_chart1, col_table1 = st.columns([1.5, 1])
            with col_chart1:
                st.write("**Biểu đồ cột thể hiện Tổng số lượng bán ra:**")
                st.bar_chart(summary_mon.set_index("Tên món")["Số_lượng_bán"])
            with col_table1:
                st.write("**Số liệu doanh thu thực tế từng món:**")
                st.dataframe(
                    summary_mon.style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("---")

            # Phân tích khung giờ vàng bán chạy trong ngày (0h - 23h)
            st.write("### ⏰ Thống kê lượng khách đặt theo Khung giờ (0h - 23h)")
            summary_gio = (
                df_anal.groupby("Giờ")
                .agg(
                    Số_lượng_món=("Số lượng", "sum"),
                    Doanh_thu=("Thành tiền", "sum"),
                )
                .reset_index()
            )

            all_hours = pd.DataFrame({"Giờ": range(24)})
            summary_gio = pd.merge(
                all_hours, summary_gio, on="Giờ", how="left"
            ).fillna(0)

            col_chart2, col_info2 = st.columns([1.5, 1])
            with col_chart2:
                st.write("**Biểu đồ lượng bán theo từng khung giờ trong ngày:**")
                st.bar_chart(summary_gio.set_index("Giờ")["Số_lượng_món"])
            with col_info2:
                st.write("**Thời điểm bán chạy nhất trong ngày:**")
                st.markdown(
                    f"👉 Khung giờ đắt khách nhất hiện tại dựa trên hóa đơn thực tế là từ **{best_hour:02d}:00 - {(best_hour+1):02d}:00** với tổng cộng **{best_hour_qty} phần** được thanh toán."
                )
                st.dataframe(
                    summary_gio[summary_gio["Số_lượng_món"] > 0].style.format(
                        {"Doanh_thu": "{:,.0f} VNĐ"}
                    ),
                    use_container_width=True,
hide_index=True,
                )

            st.markdown("---")

            # Phân tích biến động doanh thu theo tháng
            st.write("### 📅 Doanh thu bán hàng theo Tháng")
            df_anal["Tháng_Số"] = df_anal["Thời gian"].dt.month
            summary_thang = (
                df_anal.groupby(["Tháng_Số", "Tháng-Năm"])
                .agg(
                    Số_lượng_bán=("Số lượng", "sum"),
                    Doanh_thu=("Thành tiền", "sum"),
                )
                .reset_index()
                .sort_values("Tháng_Số")
            )

            col_chart3, col_table3 = st.columns([1.5, 1])
            with col_chart3:
                st.write("**Biểu đồ cột tăng trưởng doanh thu qua các tháng:**")
                st.bar_chart(summary_thang.set_index("Tháng-Năm")["Doanh_thu"])
            with col_table3:
                st.write("**Tổng doanh thu chi tiết từng tháng:**")
                st.dataframe(
                    summary_thang[
                        ["Tháng-Năm", "Số_lượng_bán", "Doanh_thu"]
                    ].style.format({"Doanh_thu": "{:,.0f} VNĐ"}),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info(
                "Chưa có dữ liệu giao dịch để thống kê. Hãy tiến hành thanh toán một vài đơn hàng trước."
            )
