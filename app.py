import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền gửi tiết kiệm",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 CÔNG CỤ TÍNH TIỀN GỬI TIẾT KIỆM")
st.caption(
    "Tính lãi theo số ngày thực tế, quy ước 1 năm = 365 ngày. "
    "Ngày gửi được tính lãi, ngày rút không tính lãi."
)


# ============================================================
# HÀM ĐỊNH DẠNG TIỀN
# ============================================================

def format_money(value):
    return f"{value:,.0f} đ".replace(",", ".")


def format_rate(value):
    return f"{value:.4f}%/năm"


# ============================================================
# TÍNH SỐ NGÀY
# ============================================================

def calculate_days(start_date, withdraw_date):
    """
    Tính từ ngày gửi đến trước ngày rút.
    
    Ví dụ:
    Gửi 01/01, rút 02/01
    => được tính 1 ngày: ngày 01/01
    
    Gửi 01/01, rút 01/02
    => được tính 31 ngày.
    """
    return (withdraw_date - start_date).days


# ============================================================
# TÍNH LÃI ĐƠN
# ============================================================

def simple_interest(principal, annual_rate, days):
    """
    Lãi đơn:
    Lãi = Gốc × Lãi suất năm × Số ngày / 365
    """
    return principal * (annual_rate / 100) * days / 365


# ============================================================
# TÍNH LÃI KÉP
# ============================================================

def compound_interest(principal, annual_rate, days):
    """
    Lãi kép theo số ngày:
    A = P × (1 + r)^(n/365)
    
    Lãi = A - P
    """
    amount = principal * (1 + annual_rate / 100) ** (days / 365)
    interest = amount - principal

    return interest, amount


# ============================================================
# TÍNH LÃI THEO THÁNG
# ============================================================

def calculate_monthly_interest(
    principal,
    annual_rate,
    start_date,
    withdraw_date,
    method,
):
    """
    Tạo bảng lãi theo từng tháng.

    Mỗi khoảng:
    - Bắt đầu từ ngày gửi / ngày đầu kỳ
    - Kết thúc trước ngày kế tiếp
    - Số ngày được tính theo thực tế.
    """

    rows = []

    current_date = start_date
    current_principal = principal

    while current_date < withdraw_date:

        # Mốc cùng ngày của tháng tiếp theo
        next_month = current_date + relativedelta(months=1)

        # Không vượt quá ngày rút
        period_end = min(next_month, withdraw_date)

        # Ngày tính lãi = từ current_date đến trước period_end
        days = (period_end - current_date).days

        if days <= 0:
            break

        if method == "Lãi đơn":
            interest = simple_interest(
                current_principal,
                annual_rate,
                days
            )

        else:
            # Lãi kép:
            # Phần lãi của riêng kỳ này
            new_amount = (
                current_principal
                * (1 + annual_rate / 100) ** (days / 365)
            )

            interest = new_amount - current_principal

        rows.append({
            "Kỳ": len(rows) + 1,
            "Từ ngày": current_date.strftime("%d/%m/%Y"),
            "Đến trước ngày": period_end.strftime("%d/%m/%Y"),
            "Số ngày": days,
            "Tiền gốc đầu kỳ": current_principal,
            "Tiền lãi": interest,
            "Gốc + lãi cuối kỳ": current_principal + interest,
        })

        # Với lãi kép, lãi được nhập vào gốc
        if method == "Lãi kép":
            current_principal += interest

        current_date = period_end

    return pd.DataFrame(rows)


# ============================================================
# GIAO DIỆN NHẬP DỮ LIỆU
# ============================================================

st.subheader("📋 Thông tin khoản tiền gửi")

col1, col2 = st.columns(2)

with col1:
    principal = st.number_input(
        "💰 Số tiền gửi",
        min_value=1_000,
        value=100_000_000,
        step=1_000_000,
        format="%.0f",
        help="Số tiền gốc khách hàng gửi."
    )

    annual_rate = st.number_input(
        "📈 Lãi suất theo năm (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.01,
        format="%.4f",
        help="Lãi suất danh nghĩa theo năm. Quy ước 1 năm = 365 ngày."
    )

    method = st.radio(
        "🧮 Hình thức tính lãi",
        ["Lãi đơn", "Lãi kép"],
        horizontal=True,
        help=(
            "Lãi kép chỉ áp dụng khi chọn nhận lãi cuối kỳ. "
            "Lãi đơn có thể áp dụng cho cả ba hình thức nhận lãi."
        )
    )


with col2:
    interest_payment = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Đầu kỳ",
        ],
        index=0,
    )

    start_date = st.date_input(
        "📅 Ngày khách hàng gửi tiền",
        value=date.today(),
        format="DD/MM/YYYY",
    )

    withdraw_date = st.date_input(
        "📅 Ngày khách hàng rút tiền",
        value=date.today() + relativedelta(months=12),
        format="DD/MM/YYYY",
    )


# ============================================================
# KIỂM TRA LÃI KÉP
# ============================================================

if method == "Lãi kép" and interest_payment != "Cuối kỳ":
    st.warning(
        "⚠️ Lãi kép chỉ được áp dụng cho hình thức nhận lãi cuối kỳ. "
        "Hệ thống sẽ chuyển sang Lãi đơn cho hình thức nhận lãi này."
    )
    calculation_method = "Lãi đơn"
else:
    calculation_method = method


# ============================================================
# KIỂM TRA NGÀY
# ============================================================

if withdraw_date <= start_date:
    st.error(
        "❌ Ngày rút tiền phải lớn hơn ngày gửi tiền."
    )
    st.stop()


# ============================================================
# TÍNH SỐ NGÀY
# ============================================================

total_days = calculate_days(
    start_date,
    withdraw_date
)


# ============================================================
# TÍNH LÃI
# ============================================================

if calculation_method == "Lãi đơn":

    total_interest = simple_interest(
        principal,
        annual_rate,
        total_days
    )

    final_amount = principal + total_interest

else:

    total_interest, final_amount = compound_interest(
        principal,
        annual_rate,
        total_days
    )


# ============================================================
# TÍNH LÃI THEO THÁNG
# ============================================================

monthly_df = calculate_monthly_interest(
    principal,
    annual_rate,
    start_date,
    withdraw_date,
    calculation_method,
)


# ============================================================
# TÍNH LÃI TRẢ ĐẦU KỲ
# ============================================================

upfront_interest = total_interest


# ============================================================
# KẾT QUẢ
# ============================================================

st.divider()

st.subheader("📊 KẾT QUẢ TÍNH TOÁN")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Tiền gốc",
        format_money(principal)
    )

with col2:
    st.metric(
        "📅 Số ngày tính lãi",
        f"{total_days:,} ngày"
    )

with col3:
    st.metric(
        "💵 Tổng tiền lãi",
        format_money(total_interest)
    )

with col4:
    st.metric(
        "🏦 Tổng nhận khi rút",
        format_money(final_amount)
    )


# ============================================================
# THÔNG TIN CHI TIẾT
# ============================================================

st.markdown("### 📌 Thông tin khoản tiền gửi")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.write(
        f"**Ngày gửi:** {start_date.strftime('%d/%m/%Y')}"
    )

    st.write(
        f"**Ngày rút:** {withdraw_date.strftime('%d/%m/%Y')}"
    )

    st.write(
        f"**Số ngày tính lãi:** {total_days:,} ngày"
    )

    st.write(
        f"**Lãi suất:** {format_rate(annual_rate)}"
    )

with info_col2:
    st.write(
        f"**Hình thức nhận lãi:** {interest_payment}"
    )

    st.write(
        f"**Phương pháp tính:** {calculation_method}"
    )

    st.write(
        f"**Tiền lãi:** {format_money(total_interest)}"
    )

    st.write(
        f"**Tổng tiền nhận:** {format_money(final_amount)}"
    )


# ============================================================
# XỬ LÝ HÌNH THỨC NHẬN LÃI
# ============================================================

st.divider()

st.subheader("💳 Phân tích hình thức nhận lãi")


if interest_payment == "Cuối kỳ":

    st.success(
        f"""
        **Khách hàng nhận lãi cuối kỳ**

        - Tiền gốc: **{format_money(principal)}**
        - Tổng tiền lãi: **{format_money(total_interest)}**
        - Tổng số tiền nhận ngày rút: **{format_money(final_amount)}**
        """
    )

elif interest_payment == "Đầu kỳ":

    st.info(
        f"""
        **Khách hàng nhận lãi đầu kỳ**

        Tiền lãi được xác định theo toàn bộ thời gian gửi:

        **{format_money(upfront_interest)}**

        Tiền gốc khách hàng nhận lại khi đến ngày rút:

        **{format_money(principal)}**

        Tổng giá trị gốc + lãi của khoản tiền gửi:

        **{format_money(final_amount)}**
        """
    )

else:

    st.info(
        f"""
        **Khách hàng nhận lãi hàng tháng**

        Tổng tiền lãi trong toàn bộ thời gian:

        **{format_money(total_interest)}**

        Tiền gốc nhận khi rút:

        **{format_money(principal)}**

        Tổng giá trị gốc + lãi:

        **{format_money(final_amount)}**
        """
    )


# ============================================================
# BẢNG LÃI HÀNG THÁNG
# ============================================================

st.divider()

st.subheader("📅 Bảng tiền lãi theo từng tháng")

if not monthly_df.empty:

    display_df = monthly_df.copy()

    display_df["Tiền gốc đầu kỳ"] = display_df[
        "Tiền gốc đầu kỳ"
    ].apply(format_money)

    display_df["Tiền lãi"] = display_df[
        "Tiền lãi"
    ].apply(format_money)

    display_df["Gốc + lãi cuối kỳ"] = display_df[
        "Gốc + lãi cuối kỳ"
    ].apply(format_money)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# TỔNG HỢP
# ============================================================

st.divider()

st.subheader("🧾 Tổng hợp khoản tiền gửi")

summary_data = {
    "Thông tin": [
        "Số tiền gửi",
        "Lãi suất năm",
        "Ngày gửi",
        "Ngày rút",
        "Số ngày tính lãi",
        "Hình thức nhận lãi",
        "Phương pháp tính",
        "Tổng tiền lãi",
        "Tổng tiền gốc + lãi",
    ],
    "Giá trị": [
        format_money(principal),
        format_rate(annual_rate),
        start_date.strftime("%d/%m/%Y"),
        withdraw_date.strftime("%d/%m/%Y"),
        f"{total_days:,} ngày",
        interest_payment,
        calculation_method,
        format_money(total_interest),
        format_money(final_amount),
    ],
}

summary_df = pd.DataFrame(summary_data)

st.table(summary_df)


# ============================================================
# GIẢI THÍCH QUY TẮC TÍNH
# ============================================================

with st.expander("ℹ️ Quy tắc tính lãi đang được sử dụng"):

    st.markdown(
        """
### 1. Quy tắc số ngày

Hệ thống tính:

**Ngày gửi → trước ngày rút**

Ví dụ:

- Gửi ngày **01/01/2026**
- Rút ngày **02/01/2026**
- Số ngày tính lãi = **1 ngày**

Ngày 01/01 được tính lãi, ngày 02/01 không tính lãi.

### 2. Lãi đơn

Lãi được tính theo số ngày thực tế:

**Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

### 3. Lãi kép

Lãi kép chỉ hoạt động khi chọn **nhận lãi cuối kỳ**.

Lãi được cộng dồn vào số tiền gốc để tiếp tục sinh lãi.

### 4. Lãi hàng tháng

Bảng chi tiết được chia thành từng khoảng tháng.

Nếu khoản gửi không tròn tháng, phần cuối cùng sẽ được tính theo số ngày thực tế.

### 5. Lãi đầu kỳ

Tiền lãi của toàn bộ thời gian gửi được xác định ngay từ đầu.

### 6. Quy ước năm

Tất cả phép tính sử dụng:

**1 năm = 365 ngày**
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏦 Công cụ tính tiền gửi tiết kiệm • "
    "Ngày gửi được tính lãi • Ngày rút không tính lãi • "
    "Quy ước 365 ngày/năm"
)
