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

    # Sidebar untuk memilih tipe chart
    st.sidebar.title("Kontrol Visualisasi")
    visualisasi_type = st.sidebar.selectbox(
        "Pilih dataset",
        ["Adventure Work", "Scrapping IMDB"]
    )
    chart_type = st.sidebar.selectbox(
        "Pilih tipe chart",
        ["Comparison", "Distribution", "Composition", "Relationship"]
    )

    if visualisasi_type == "Adventure Work":
        st.title("Visualisasi Penjualan Adventure Work")

        # Buat koneksi ke database
        mydb = get_db_connection()
        
        if mydb is not None:
            # 1. COMPARISON - BAR CHART
            if chart_type == "Comparison":
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

            # 2. DISTRIBUTION - SCATTER PLOT
            elif chart_type == "Distribution":
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

            # 3. COMPOSITION - DONUT CHART
            elif chart_type == "Composition":
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

            # 4. RELATIONSHIP - SCATTER PLOT
            elif chart_type == "Relationship":
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
   
    elif visualisasi_type == "Scrapping IMDB":
        st.title("Visualisasi Film Produksi Walt Disney Tahun 2023") 

        # Load data
        data = pd.read_csv("imdb_walt_disney.csv")

        # 1. COMPARISON - BAR CHART
        if chart_type == "Comparison":
            st.header("Bar Chart - Perbandingan Budget dari Setiap Film")
            
            # Clean 'Open_Week_Date' to ensure it only contains date information
            data['Open_Week_Date'] = data['Open_Week_Date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
            
            # Convert 'Open_Week_Date' to datetime
            data['Open_Week_Date'] = pd.to_datetime(data['Open_Week_Date'], format="%Y-%m-%d")
            
            # Create bar chart for budget comparison
            fig = px.bar(data, x='Name', y='Budget',
                         labels={'Budget': 'Budget (in USD)', 'Name': 'Movie Name'})
            
            # Display chart
            st.plotly_chart(fig)
        
        
        # 2. DISTRIBUTION - SCATTER PLOT
        elif chart_type == "Distribution":
            st.header("Scatter Plot - Distribusi Gross US dan Gross World dari Setiap Film")
            
            # Drop rows with missing values
            data = data.dropna(subset=['Gross_US', 'Gross_World'])
            
            # Create scatter plot for both Gross_US and Gross_World
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=data['Name'],
                y=data['Gross_US'],
                mode='markers',
                name='Gross US',
                marker=dict(size=10, color='blue'),
                text=data[['Budget', 'Opening_Week', 'Open_Week_Date']]
            ))
            
            fig.add_trace(go.Scatter(
                x=data['Name'],
                y=data['Gross_World'],
                mode='markers',
                name='Gross World',
                marker=dict(size=10, color='red'),
                text=data[['Budget', 'Opening_Week', 'Open_Week_Date']]
            ))
            
            fig.update_layout(
                xaxis_title='Movie Name',
                yaxis_title='Gross (in USD)',
                hovermode='closest'
            )
            
            # Display chart
            st.plotly_chart(fig)
        
        
        # 3. COMPOSITION - DONUT CHART
        elif chart_type == "Composition":
            st.header("Donut Chart - Komposisi Rating Film")
            
            # Drop rows with missing rating values
            data = data.dropna(subset=['Rating'])
                    
            # Create a donut chart for the rating distribution
            rating_counts = data['Rating'].value_counts().reset_index()
            rating_counts.columns = ['Rating', 'Count']
                     
            fig = px.pie(rating_counts, values='Count', names='Rating', hole=0.4)
                    
            # Display chart
            st.plotly_chart(fig)
        
        # 4. RELATIONSHIP - SCATTER PLOT
        elif chart_type == "Relationship":
            st.header("Scatter Plot - Hubungan antara Durasi dan Budget Film")
            
            # Drop rows with missing values in 'Duration' or 'Budget'
            data = data.dropna(subset=['Durasi(Menit)', 'Budget'])
            
            # Create scatter plot for Duration vs Budget
            fig = px.scatter(data, x='Durasi(Menit)', y='Budget', labels={'Duration': 'Duration (minutes)', 'Budget': 'Budget (USD)'})
            
            # Display chart
            st.plotly_chart(fig)
        

if __name__ == "__main__":
    main()
