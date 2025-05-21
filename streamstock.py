import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Set up page
st.set_page_config(page_title="📈 Stock Analytics MySQL Dashboard", layout="wide")

# Connect to MySQL
@st.cache_resource
def get_connection():
    engine = create_engine("mysql+pymysql://root:Mysqlpass123@localhost:3306/STOCKS")
    return engine

engine = get_connection()

# Load data from MySQL tables
@st.cache_data
def load_table(table_name):
    return pd.read_sql(f"SELECT * FROM `{table_name}`", engine)

tables = {
    "Top 5 Gainers": "Top_5_Gainers",
    "Top 5 Losers": "Top_5_Losers",
    "Volatile Stocks": "Volatile",
    "Sector Performance": "Sector_performance",
    "Cumulative Returns": "Top5_cumulative_returns",
    "Correlation Matrix": "Correlation_Stock_Price"
}

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color:limegreen;'>📊 STOCK DASHBOARD</h1>", unsafe_allow_html=True)
    selected_section = st.selectbox("Choose Analysis Type", list(tables.keys()))

st.title(f"📌 {selected_section}")
df = load_table(tables[selected_section])

# Section-wise Display
if selected_section == "Top 5 Gainers":
    st.dataframe(df)
    
    month_list = sorted(df["Month_Year"].astype(str).unique())
    selected_month = st.selectbox("Select Month (YYYY-MM):", month_list)

    top_gainers = df.sort_values(by='Monthly_Return', ascending=False).head(6)
    fig = px.bar(top_gainers, x='ticker', y='Monthly_Return', color='Monthly_Return', title='Top 5 Gainers', hover_name='ticker',
             color_continuous_scale=px.colors.sequential.Greens)
    fig.update_layout(xaxis_title="Stock Ticker", yaxis_title="Gainers Level")
    st.plotly_chart(fig, use_container_width=True)

    ######

elif selected_section == "Top 5 Losers":
    st.dataframe(df)

    month_list = sorted(df["Month_Year"].astype(str).unique())
    selected_month = st.selectbox("Select Month (YYYY-MM):", month_list)

    top_losers = df.sort_values(by='Monthly_Return', ascending=True).head(6)
    fig = px.bar(top_losers, x='ticker', y='Monthly_Return', color='Monthly_Return', title='Top 5 Losers', hover_name='ticker',
             color_continuous_scale=px.colors.sequential.Reds)
    fig.update_layout(xaxis_title="Stock Ticker", yaxis_title="Losers Level")

    st.plotly_chart(fig, use_container_width=True)


elif selected_section == "Volatile Stocks":
    st.dataframe(df)
       
    fig = px.bar(df, x='ticker', y='volatility', color='volatility', 
             title='Volatile Stocks', hover_name='ticker',
             color_continuous_scale=px.colors.sequential.Viridis_r)

    fig.update_layout(xaxis_title="Stock Ticker", yaxis_title="Volatility Level")

    st.plotly_chart(fig, use_container_width=True)

elif selected_section == "Sector Performance":
    st.dataframe(df)

    # Plotly Bar Chart
    fig = px.bar(df, x="sector", y="Overall Return (%)", color="Overall Return (%)", title="Sector Performance")

    # Seaborn Bar Chart
    plt.figure(figsize=(15, 4))
    sns.barplot(x="sector", y="Overall Return (%)", data=df, palette="viridis")
    plt.xticks(rotation=90)
    plt.title("Average Yearly Return by Sector")
    plt.xlabel("Sector")
    plt.ylabel("Average Yearly Return")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Display in Streamlit
    st.pyplot(plt)
############################

elif selected_section == "Cumulative Returns":    

    st.title("📈 Stock Cumulative Returns Dashboard")

    # Load your CSV
    df_all = pd.read_csv(r"C:\Users\Velpr\Documents\Stock_P2\Top5_cumulative_returns.csv", parse_dates=['date'])

    # Check basic structure
    if 'ticker' not in df_all.columns or 'close' not in df_all.columns:
        st.error("CSV file must contain at least 'ticker', 'date', and 'close' columns.")
        st.stop()

    # Sidebar for ticker selection
    tickers = df_all['ticker'].unique()
    selected_tickers = st.sidebar.multiselect("Select Tickers", tickers, default=tickers[:1])

    # Filter data by selected tickers
    filtered_df = df_all[df_all['ticker'].isin(selected_tickers)]

    # Sort before calculating returns
    filtered_df = filtered_df.sort_values(by=['ticker', 'date'])

    # Calculate daily return
    filtered_df['daily_return'] = filtered_df.groupby('ticker')['close'].pct_change()

    # Calculate cumulative return
    #filtered_df['Cumulative_return'] = filtered_df.groupby('ticker')['daily_return'].apply(lambda x: (1 + x).cumprod() - 1)
    filtered_df['Cumulative_return'] = filtered_df.groupby('ticker')['daily_return'].transform(lambda x: (1 + x).cumprod() - 1)

    # Plot
    plt.figure(figsize=(12, 6))
    for tick in selected_tickers:
        df = filtered_df[filtered_df['ticker'] == tick]
        sns.lineplot(data=df, x='date', y='Cumulative_return', label=tick, linewidth=1.0)

    plt.title("Cumulative Returns Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend(title='TICKER', fontsize=10, title_fontsize=12)
    plt.grid(True, linestyle='--', linewidth=1.5, alpha=0.6)
    plt.tight_layout()
    st.pyplot(plt.gcf())


#############################

elif selected_section == "Correlation Matrix":
    st.dataframe(df)
    df_numeric = df.select_dtypes(include='number')
    fig, ax = plt.subplots(figsize=(20, 16))
    sns.heatmap(df_numeric.corr(), annot=True,  cmap='coolwarm', annot_kws={"size": 6}, linewidths=0.5, cbar=True,square=True)
    
    plt.title('Stock Price Correlation Heatmap', fontsize=20)
    plt.xticks(rotation=90)       
    plt.yticks(rotation=0)        
    plt.tight_layout()
    plt.show()

    st.pyplot(fig)
#############

    




