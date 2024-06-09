import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

def get_data_from_db():
    mydb = mysql.connector.connect(
        host="localhost",  # ganti dengan host database Anda
        user="root",       # ganti dengan user database Anda
        password="",       # ganti dengan password database Anda
        database="aw"      # ganti dengan nama database Anda
    )

    query = """
    SELECT
      c.CountryRegionName AS CustomerCountry,
      SUM(fis.SalesAmount) AS TotalSalesAmount
    FROM
      factinternetsales fis
    JOIN
      dimcustomer c ON fis.CustomerKey = c.CustomerKey
    GROUP BY
      c.CountryRegionName;
    """
    df = pd.read_sql(query, mydb)
    mydb.close()
    return df

# Data fetching
df = get_data_from_db()

# Streamlit app
st.title('Komposisi Total Sales Amount Berdasarkan Negara Pelanggan')

# Plotting donut chart
fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(df['TotalSalesAmount'], labels=df['CustomerCountry'], autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.3})

# Donut chart
center_circle = plt.Circle((0,0),0.70,fc='white')
fig.gca().add_artist(center_circle)

# Menyesuaikan font size
for text in texts + autotexts:
    text.set_fontsize(12)

plt.title('Komposisi Total Sales Amount Berdasarkan Negara Pelanggan')
st.pyplot(fig)
