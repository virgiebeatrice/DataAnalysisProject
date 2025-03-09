import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px

st.title("Dashboard Brazilian E-Commerce")
@st.cache_data
def load_data():
    merged_data = pd.read_csv(r"C:\Users\User\Downloads\Proyek Analisis Data\Dashboard\merged_data1.csv", parse_dates=['order_purchase_timestamp'])
    
    # Buat kolom tambahan
    merged_data['order_year_month'] = merged_data['order_purchase_timestamp'].dt.to_period('M').astype(str)
    merged_data['order_year'] = merged_data['order_purchase_timestamp'].dt.year
    merged_data['order_month'] = merged_data['order_purchase_timestamp'].dt.month
    merged_data['day_of_week'] = merged_data['order_purchase_timestamp'].dt.day_name()
    merged_data['order_hour'] = merged_data['order_purchase_timestamp'].dt.hour

    # Fungsi untuk kategori waktu pemesanan
    def categorize_time(hour):
        if 0 <= hour < 6:
            return "Dawn"
        elif 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 15:
            return "Noon"
        elif 15 <= hour < 18:
            return "Evening"
        else:
            return "Night"

    merged_data['order_time_category'] = merged_data['order_hour'].apply(categorize_time)
    
    return merged_data

# Load data
df = load_data()

# Sidebar Filter
st.sidebar.header("Filter Data")
selected_year = st.sidebar.radio("Pilih Tahun", sorted(df['order_year'].dropna().unique()), index=0)
selected_month = st.sidebar.radio("Pilih Bulan", range(1, 13), index=0)

# Filter Data Berdasarkan Pilihan
filtered_df = df[(df['order_year'] == selected_year) & (df['order_month'] == selected_month)]

# Total Revenue & Total Orders
total_revenue = filtered_df['payment_value'].sum() if not filtered_df.empty else 0
total_orders = filtered_df['order_id'].nunique() if not filtered_df.empty else 0

# Menampilkan Total Revenue & Total Orders
col1, col2 = st.columns(2)
col1.metric("Total Revenue", format_currency(total_revenue, 'BRL', locale='pt_BR'))
col2.metric("Total Orders", f"{total_orders:,}")

# Kategori Terlaris & Terburuk
col3, col4 = st.columns(2)

if not filtered_df.empty:
    category_counts = filtered_df['product_category_name'].value_counts()
    
    top_categories = category_counts.nlargest(5)
    worst_categories = category_counts.nsmallest(5)

    # Ukuran Pie Chart Sama & Hanya Menampilkan Persentase
    pie_size = {"height": 400, "width": 400, "showlegend": False}

    fig1 = px.pie(names=top_categories.index, values=top_categories.values, title="5 Kategori Terlaris", hole=0.4)
    fig1.update_layout(**pie_size)
    fig1.update_traces(textinfo="percent")

    fig2 = px.pie(names=worst_categories.index, values=worst_categories.values, title="5 Kategori Terburuk", hole=0.4)
    fig2.update_layout(**pie_size)
    fig2.update_traces(textinfo="percent")

    col3.plotly_chart(fig1)
    col4.plotly_chart(fig2)
else:
    col3.warning("Tidak ada data kategori terlaris bulan ini.")
    col4.warning("Tidak ada data kategori terburuk bulan ini.")

# Metode Pembayaran Terpopuler
if not filtered_df.empty:
    payment_counts = filtered_df['payment_type'].value_counts()
    if not payment_counts.empty:
        fig3 = px.bar(x=payment_counts.index, y=payment_counts.values, title="Metode Pembayaran Terpopuler",
                      labels={'x': 'Metode Pembayaran', 'y': 'Jumlah'})
        st.plotly_chart(fig3)
    else:
        st.warning("Tidak ada data metode pembayaran untuk bulan ini.")
else:
    st.warning("Tidak ada data pembayaran untuk periode ini.")

# Urutan hari dan waktu
day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
time_order = ["Dawn", "Morning", "Noon", "Evening", "Night"]

# Visualisasi Orders per Day
if not filtered_df.empty:
    day_counts = filtered_df['day_of_week'].value_counts().reindex(day_order).fillna(0)
    fig1 = px.bar(x=day_counts.index, y=day_counts.values, 
                  title="Orders per Day", labels={'x': 'Day of the Week', 'y': 'Orders'}, color=day_counts.index, 
                  color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig1)

    # Visualisasi Orders per Time of Day
    time_counts = filtered_df['order_time_category'].value_counts().reindex(time_order).fillna(0)
    fig2 = px.bar(x=time_counts.index, y=time_counts.values, 
                  title="Orders per Time of Day", labels={'x': 'Time of Day', 'y': 'Orders'}, color=time_counts.index, 
                  color_discrete_sequence=px.colors.sequential.Oranges)
    st.plotly_chart(fig2)
else:
    st.warning("Tidak ada data untuk periode ini.")

# Grafik Tren Penjualan Harian
prev_month = selected_month - 1 if selected_month > 1 else 12
prev_year = selected_year if selected_month > 1 else selected_year - 1

trend_df = df[((df['order_year'] == selected_year) & (df['order_month'] == selected_month)) |
              ((df['order_year'] == prev_year) & (df['order_month'] == prev_month))]

if not trend_df.empty:
    daily_orders = trend_df.groupby(trend_df['order_purchase_timestamp'].dt.date).size().reset_index(name="order_counts")
    fig4 = px.line(daily_orders, x="order_purchase_timestamp", y="order_counts", title="Tren Penjualan Harian")
    st.plotly_chart(fig4)
else:
    st.warning("Tidak ada data tren penjualan untuk bulan ini.")
