import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Loan System", layout="wide")

FILE_NAME = "loan_reports.xlsx"

# -----------------------------
# 🎨 PROFESSIONAL FINTECH UI THEME
# -----------------------------
st.markdown("""
    <style>

    /* Soft fintech gradient background */
    body {
        background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
    }

    /* Main container (glass effect) */
    .main {
        background: rgba(255, 255, 255, 0.92);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }

    h1 {
        text-align: center;
        color: #ffffff;
        font-weight: 700;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1c2b, #2c3e50);
        color: white;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border-radius: 10px;
        height: 3em;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        transition: 0.2s;
    }

    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
        margin-bottom: 12px;
    }

    /* Success/Error */
    .success {
        color: #00c853;
        font-size: 18px;
        font-weight: bold;
    }

    .error {
        color: #ff3d00;
        font-size: 18px;
        font-weight: bold;
    }

    /* Dataframe styling */
    .stDataFrame {
        background: white;
        border-radius: 10px;
    }

    </style>
""", unsafe_allow_html=True)

st.title("🏦 Smart Loan Eligibility & Bank Comparison System")

# -----------------------------
# FUNCTIONS
# -----------------------------

def credit_score(income, emi, emp):
    score = 650

    if income > 150000:
        score += 120
    elif income > 75000:
        score += 80
    elif income > 40000:
        score += 40

    if emi > income * 0.4:
        score -= 80

    if emp in ["Self-employed", "Business Owner"]:
        score -= 20

    return max(300, min(score, 900))


def emi_calc(P, rate, n):
    r = rate / (12 * 100)
    return P * r * (1 + r)**n / ((1 + r)**n - 1)


def interest_calc(emi, P, n):
    total = emi * n
    return total, total - P


def eligibility(age, income, emi):
    if age < 21:
        return False, 0, 0

    max_emi = income * 0.45
    avail = max_emi - emi

    if avail <= 0:
        return False, 0, 0

    return True, max_emi, avail


def loan_amount(emi, rate, n):
    r = rate / (12 * 100)
    return emi * ((1 + r)**n - 1) / (r * (1 + r)**n)


def documents(loan_type, emp):
    docs = ["Aadhaar Card", "PAN Card", "Photo"]

    if emp == "Salaried":
        docs += ["Salary Slips", "Bank Statement"]
    else:
        docs += ["ITR", "Business Proof"]

    if loan_type == "Home Loan":
        docs += ["Property Documents"]
    elif loan_type in ["CC", "OD"]:
        docs += ["Business Financials"]

    return docs


def compare_banks(avail, months):
    banks = {
        "SBI": 8.5,
        "HDFC": 9.0,
        "ICICI": 9.2,
        "Axis": 9.5
    }

    data = []

    for bank, rate in banks.items():
        loan = loan_amount(avail, rate, months)
        emi = emi_calc(loan, rate, months)
        total, interest = interest_calc(emi, loan, months)

        data.append({
            "Bank": bank,
            "Interest Rate (%)": rate,
            "Loan Amount (₹)": round(loan, 2),
            "EMI (₹)": round(emi, 2),
            "Total Interest (₹)": round(interest, 2),
            "Total Payment (₹)": round(total, 2)
        })

    return pd.DataFrame(data)


# -----------------------------
# EXCEL REPORT SYSTEM
# -----------------------------

def save_excel(record):
    df_new = pd.DataFrame([record])

    if os.path.exists(FILE_NAME):
        df_old = pd.read_excel(FILE_NAME)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_excel(FILE_NAME, index=False)


def download_excel():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "rb") as f:
            st.download_button(
                "📥 Download Excel Report",
                f,
                "Loan_Report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# -----------------------------
# INPUT
# -----------------------------

st.sidebar.header("📋 User Input")

name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", 18, 70, 25)
income = st.sidebar.number_input("Monthly Income", value=50000)

employment = st.sidebar.selectbox(
    "Employment Type",
    ["Salaried", "Self-employed", "Business Owner", "Professional", "Freelancer"]
)

loan_type = st.sidebar.selectbox(
    "Loan Type",
    ["Home Loan", "Personal Loan", "Car Loan", "CC", "OD"]
)

existing_emi = st.sidebar.number_input("Existing EMI", value=0)
years = st.sidebar.slider("Tenure (Years)", 1, 30, 5)

months = years * 12

# -----------------------------
# MAIN EXECUTION
# -----------------------------

if st.sidebar.button("🚀 Check Eligibility"):

    score = credit_score(income, existing_emi, employment)
    eligible, max_emi, avail = eligibility(age, income, existing_emi)

    st.markdown(f"<div class='card'>📊 Credit Score: <b>{score}</b></div>", unsafe_allow_html=True)

    if not eligible:
        st.markdown("<div class='error'>❌ Not Eligible for Loan</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='success'>✅ Eligible for Loan</div>", unsafe_allow_html=True)

        df = compare_banks(avail, months)

        st.subheader("🏦 Bank Comparison")
        st.dataframe(df)

        best = df.loc[df["EMI (₹)"].idxmin()]

        st.markdown(f"""
        <div class='card'>
        🏆 <b>Best Bank:</b> {best['Bank']} <br>
        📊 <b>Interest Rate:</b> {best['Interest Rate (%)']}% <br>
        💰 <b>Loan Amount:</b> ₹{best['Loan Amount (₹)']} <br>
        📉 <b>EMI:</b> ₹{best['EMI (₹)']}
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📄 Required Documents")
        for d in documents(loan_type, employment):
            st.write("✔", d)

        st.subheader("📊 EMI Chart")
        st.bar_chart(df.set_index("Bank")["EMI (₹)"])

        # SAVE RECORD
        record = {
            "Name": name,
            "Age": age,
            "Income": income,
            "Employment": employment,
            "Loan Type": loan_type,
            "Credit Score": score,
            "Best Bank": best["Bank"],
            "Interest Rate": best["Interest Rate (%)"],
            "Loan Amount": best["Loan Amount (₹)"],
            "EMI": best["EMI (₹)"]
        }

        save_excel(record)

# -----------------------------
# DOWNLOAD SECTION
# -----------------------------

st.subheader("📊 Download Reports")
download_excel()