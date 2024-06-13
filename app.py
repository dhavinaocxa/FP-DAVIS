import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Fungsi untuk membuat koneksi ke database
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="kubela.id",
            user="davis2024irwan",
            password="wh451n9m@ch1n3",
            database="aw"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None

# Fungsi untuk mengambil data untuk line chart
def get_line_data(mydb):
    if mydb is None:
        return None
    try:
        query = """
        SELECT
          DATE_FORMAT(OrderDateKey, '%Y-%m') AS Month,
          SUM(SalesAmount) AS TotalSales,
          YEAR(OrderDateKey) AS Year
        FROM
          factinternetsales
        GROUP BY
          YEAR(OrderDateKey), DATE_FORMAT(OrderDateKey, '%Y-%m')
        ORDER BY
          Year, Month;
        """
        df = pd.read_sql(query, mydb)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Fungsi untuk mengambil data untuk scatter plot
def get_scatter_data(mydb):
    if mydb is None:
        return None
    try:
        query = """
        SELECT
          OrderDateKey,
          SUM(SalesAmount) AS TotalSalesAmount
        FROM
          factinternetsales
        GROUP BY
          OrderDateKey;
        """
        df = pd.read_sql(query, mydb)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Fungsi untuk mengambil data untuk donut chart
def get_donut_data(mydb):
    if mydb is None:
        return None
    try:
        query = """
        SELECT
          st.SalesTerritoryRegion,
          SUM(fis.SalesAmount) AS TotalSalesAmount
        FROM
          factinternetsales fis
        JOIN
          dimsalesterritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
        GROUP BY
          st.SalesTerritoryRegion;
        """
        df = pd.read_sql(query, mydb)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Fungsi untuk mengambil data untuk scatter plot baru
def get_scatter2_data(mydb):
    if mydb is None:
        return None
    try:
        query = """
        SELECT
          dc.YearlyIncome,
          SUM(fis.SalesAmount) AS TotalSalesAmount
        FROM
          factinternetsales fis
        JOIN
          dimcustomer dc ON fis.CustomerKey = dc.CustomerKey
        GROUP BY
          dc.YearlyIncome;
        """
        df = pd.read_sql(query, mydb)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Main Streamlit App
def main():
    st.title("Visualisasi Penjualan Adventure Work")
    
    # Sidebar untuk memilih tipe chart
    st.sidebar.title("Kontrol Visualisasi")
    chart_type = st.sidebar.selectbox(
        "Pilih tipe chart",
        ["Line Chart", "Scatter Plot", "Donut Chart", "Scatter Plot (Income vs Sales)"]
    )
    
    # Buat koneksi ke database
    mydb = get_db_connection()
    
    if mydb is not None:
        if chart_type == "Line Chart":
            st.header("Line Chart - Perbandingan Penjualan Bulanan")
            df_line = get_line_data(mydb)
            if df_line is not None:
                # Konversi kolom 'Month' ke datetime
                df_line['Month'] = pd.to_datetime(df_line['Month'])
                
                # Plot menggunakan plotly untuk visualisasi interaktif
                fig_line = px.line(
                    df_line,
                    x='Month',
                    y='TotalSales',
                    color='Year',
                    labels={'TotalSales':'Total Sales', 'Month':'Bulan'},
                )
                
                # Update layout for smaller scale
                fig_line.update_layout(
                    autosize=False,
                    width=800,  # Set width here
                    height=400  # Set height here
                )
                
                st.plotly_chart(fig_line)

        elif chart_type == "Scatter Plot":
            st.header("Scatter Plot - Distribusi Total Sales Berdasarkan OrderDateKey")
            df_scatter = get_scatter_data(mydb)
            if df_scatter is not None:
                fig_scatter = px.scatter(
                    df_scatter,
                    x='OrderDateKey',
                    y='TotalSalesAmount',
                    labels={'OrderDateKey':'Order Date Key', 'TotalSalesAmount':'Total Sales Amount'}
                )
                st.plotly_chart(fig_scatter)
                
        elif chart_type == "Donut Chart":
            st.header("Donut Chart - Komposisi Total Sales Berdasarkan Wilayah")
            df_donut = get_donut_data(mydb)
            if df_donut is not None:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=df_donut['SalesTerritoryRegion'],
                    values=df_donut['TotalSalesAmount'],
                    hole=0.3,
                    textinfo='label+percent'
                )])
                st.plotly_chart(fig_donut)

        elif chart_type == "Scatter Plot (Income vs Sales)":
            st.header("Scatter Plot - Hubungan antara Pendapatan Tahunan dan Jumlah Penjualan")
            df_scatter2 = get_scatter2_data(mydb)
            if df_scatter2 is not None:
                fig_scatter2 = px.scatter(
                    df_scatter2,
                    x='YearlyIncome',
                    y='TotalSalesAmount',
                    labels={'YearlyIncome':'Pendapatan Tahunan (YearlyIncome)', 'TotalSalesAmount':'Jumlah Penjualan (TotalSalesAmount)'}
                )
                st.plotly_chart(fig_scatter2)

        # Tutup koneksi ke database
        mydb.close()
    else:
        st.error("Could not connect to the database. Please check your database connection settings.")

if __name__ == "__main__":
    main()
