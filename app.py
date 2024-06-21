import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Data Visualisasi Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Fungsi untuk membuat koneksi ke database
def get_db_connection():
    try:
        connection = st.connection("mydb", type="sql", autocommit=True)
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
    st.sidebar.title("📊 Dashboard")
    visualisasi_type = st.sidebar.selectbox(
        "Select dataset",
        ["Adventure Work", "Scrapping IMDB"]
    )
    chart_type = st.sidebar.selectbox(
        "Select chart type",
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
                        width=800, 
                        height=400 
                    )
                    
                    st.plotly_chart(fig_line)

                # Penjelasan chart
                with st.expander('About Chart', expanded=True):
                    st.write('''
                         - Data: Database Adventure Work
                         - Visualisasi ini menggambarkan perbandingan jumlah penjualan Adventure Work di setiap bulannya. Dapat disimpulkan sempat terjadi kenaikan dari bulan Juli hingga bulan Oktober namun terjadi penurunan yang cukup drastis dari bulan Oktober ke bulan November.
                         ''')

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

                # Penjelasan chart
                with st.expander('About Chart', expanded=True):
                    st.write('''
                         - Data: Database Adventure Work
                         - Visualisasi ini menggambarkan bagaimana penjualan berfluktuasi sepanjang waktu. Dapat disimpulkan terjadi peningkatan penjualan pada tahun-tahun terakhir.
                         ''')

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

                # Penjelasan chart
                with st.expander('About Chart', expanded=True):
                    st.write('''
                         - Data: Database Adventure Work
                         - Visualisasi ini menggambarkan bagaimana penjualan didistribusikan di berbagai area geografis yang dapat membantu dalam analisis kinerja regional dan pengambilan keputusan strategis kedepannya.
                         ''')

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

                # Penjelasan chart
                with st.expander('About Chart', expanded=True):
                    st.write('''
                         - Data: Database Adventure Work
                         - Visualisasi ini menggambarkan hubungan pendapatan tahunan pelanggan dengan jumlah penjualan yang dilakukan pelanggan tersebut. Dapat disimpulkan target pasar perusahaan ini merupakan pelanggan dengan golongan ekonomi menengah kebawah.
                         ''')
    
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
            
            data['Open_Week_Date'] = data['Open_Week_Date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
            data['Open_Week_Date'] = pd.to_datetime(data['Open_Week_Date'], format="%Y-%m-%d")
            
            # Membuat bar chart untuk perbandingan budget
            fig = px.bar(data, x='Name', y='Budget',
                         labels={'Budget': 'Budget (in USD)', 'Name': 'Movie Name'})
            
            # Tampilkan chart
            st.plotly_chart(fig)

            # Penjelasan chart
            with st.expander('About Chart', expanded=True):
                st.write('''
                     - Data: [Scrapping IMDB](https://www.imdb.com/search/title/?title_type=feature&release_date=2023-01-01,2023-12-31&companies=disney&sort=num_votes,desc)
                     - Visualisasi ini menggambarkan bagaimana anggaran dialokasikan di berbagai proyek film yang dapat membantu dalam analisis, pengambilan keputusan, dan pemahaman yang lebih baik tentang alokasi anggaran dalam produksi film.
                     ''')
        
        
        # 2. DISTRIBUTION - SCATTER PLOT
        elif chart_type == "Distribution":
            st.header("Scatter Plot - Distribusi Gross US dan Gross World dari Setiap Film")
            
            # Membuat scatter plot untuk Gross US dan Gross World
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
            
            # Tampilkan chart
            st.plotly_chart(fig)

            # Penjelasan chart
            with st.expander('About Chart', expanded=True):
                st.write('''
                     - Data: [Scrapping IMDB](https://www.imdb.com/search/title/?title_type=feature&release_date=2023-01-01,2023-12-31&companies=disney&sort=num_votes,desc)
                     - Visualisasi ini berfungsi untuk memahami seberapa sukses film tersebut dalam mencapai pasar domestik dan internasional.
                     ''')
        
        
        # 3. COMPOSITION - DONUT CHART
        elif chart_type == "Composition":
            st.header("Donut Chart - Komposisi Rating Film")
        
            data = data.dropna(subset=['Rating'])
                    
            # Membuat donut chart untuk komposisi rating
            rating_counts = data['Rating'].value_counts().reset_index()
            rating_counts.columns = ['Rating', 'Count']
                     
            fig = px.pie(rating_counts, values='Count', names='Rating', hole=0.4)
                    
            # Tampilkan chart
            st.plotly_chart(fig)

            # Penjelasan chart
            with st.expander('About Chart', expanded=True):
                st.write('''
                     - Data: [Scrapping IMDB](https://www.imdb.com/search/title/?title_type=feature&release_date=2023-01-01,2023-12-31&companies=disney&sort=num_votes,desc)
                     - Visualisasi ini menggambarkan komposisi rating film yang diproduksi oleh Walt Disney pada tahun 2023. 
                     ''')
        
        # 4. RELATIONSHIP - SCATTER PLOT
        elif chart_type == "Relationship":
            st.header("Scatter Plot - Hubungan antara Durasi dan Budget Film")
            
            # Membuat scatter plot untuk hubungan durasi dan budget film
            fig = px.scatter(data, x='Durasi(Menit)', y='Budget', labels={'Duration': 'Duration (minutes)', 'Budget': 'Budget (USD)'})
            
            # Tampilkan chart
            st.plotly_chart(fig)

            # Penjelasan chart
            with st.expander('About Chart', expanded=True):
                st.write('''
                     - Data: [Scrapping IMDB](https://www.imdb.com/search/title/?title_type=feature&release_date=2023-01-01,2023-12-31&companies=disney&sort=num_votes,desc)
                     - Visualisasi ini menggambarkan bagaimana alokasi anggaran terkait dengan durasi film. Dapat disimpulkan semakin lama durasi film maka semakin banyak budget yang dikeluarkan untuk memproduksi film tersebut.
                     ''')
        

if __name__ == "__main__":
    main()
