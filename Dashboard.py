import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Vehicle Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== DATA LOADING ======================
@st.cache_data
def load_data():
    file_path = 'synthetic_vehicle_dataset.csv'
    if not os.path.exists(file_path):
        st.error(f"Dataset not found at {file_path}. Please check the file path.")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df['Billing_Date'] = pd.to_datetime(df['Billing_Date'], dayfirst=True)
    df['Billing_Quantity'] = df['Billing_Quantity'].astype(float).round(0).astype(int)
    df['Material_ID'] = df['Material_ID'].astype(str)
    df['Customer_ID'] = df['Customer_ID'].astype(str)
    
    # Precompute common time-based features
    df['YearMonth'] = df['Billing_Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Billing_Date'].dt.day_name()
    df['Month'] = df['Billing_Date'].dt.month_name()
    df['Year'] = df['Billing_Date'].dt.year
    df['DayType'] = df['Billing_Date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    
    return df

df = load_data()

if df.empty:
    st.stop()

# ====================== SIDEBAR ======================
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("Use these filters to update all pages.")

min_date = df['Billing_Date'].min().date()
max_date = df['Billing_Date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

selected_materials = st.sidebar.multiselect(
    "Filter Materials", 
    options=sorted(df['Material_ID'].unique()),
    default=[]
)

selected_customers = st.sidebar.multiselect(
    "Filter Customers", 
    options=sorted(df['Customer_ID'].unique()),
    default=[]
)

# Store selected filters in session state so pages can access them
st.session_state['date_range'] = date_range
st.session_state['selected_materials'] = selected_materials
st.session_state['selected_customers'] = selected_customers

# ====================== FILTER DATA FOR GLOBAL DISPLAY ======================
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['Billing_Date'].dt.date >= start_date) & (df['Billing_Date'].dt.date <= end_date)
else:
    mask = df['Billing_Date'].dt.date == date_range[0]

if selected_materials:
    mask &= df['Material_ID'].isin(selected_materials)
if selected_customers:
    mask &= df['Customer_ID'].isin(selected_customers)

filtered_df = df[mask]
st.session_state['filtered_df'] = filtered_df

# ====================== MAIN PAGE ======================
st.title("🚗 Vehicle Parts Billing Dashboard")
st.markdown("""
Welcome to the Vehicle Parts Billing Dashboard. This application provides insights into 
billing quantities, customer behavior, and operational patterns. Use the sidebar to filter 
data, and navigate through the pages on the left for detailed visual analysis.
""")

st.subheader("Key Performance Indicators (Filtered)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Records", f"{len(filtered_df):,}")
col2.metric("Total Quantity", f"{filtered_df['Billing_Quantity'].sum():,}")
col3.metric("Unique Customers", f"{filtered_df['Customer_ID'].nunique():,}")
col4.metric("Unique Materials", f"{filtered_df['Material_ID'].nunique():,}")
col5.metric("Avg Quantity/Transaction", f"{filtered_df['Billing_Quantity'].mean():.2f}")

st.divider()

st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(100), use_container_width=True)

st.markdown("---")
st.caption("Data is synced across all pages. Please use the sidebar to navigate.")
