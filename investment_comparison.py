import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from matplotlib.ticker import FuncFormatter

# Define function to fetch and process data
@st.cache_data
def fetch_data():
    # Fetch historical data for S&P 500 ETF (VOO), VWO ETF, US T-Bonds ETF (IEF), CAD-USD exchange rate, TSX index fund (XIU), and Nifty index fund (INDY)
    s_p500_etf = yf.download('VOO', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    vwo_etf = yf.download('VWO', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    t_bonds_etf = yf.download('IEF', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    cad_usd = yf.download('CADUSD=X', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    tsx_etf = yf.download('XIU.TO', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    nifty_etf = yf.download('INDY', start='2021-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1mo')['Adj Close']
    
    return s_p500_etf, vwo_etf, t_bonds_etf, cad_usd, tsx_etf, nifty_etf

# Load data
s_p500_etf, vwo_etf, t_bonds_etf, cad_usd, tsx_etf, nifty_etf = fetch_data()

# Convert index to datetime.date for Streamlit slider compatibility
s_p500_etf.index = s_p500_etf.index.to_pydatetime()
vwo_etf.index = vwo_etf.index.to_pydatetime()
t_bonds_etf.index = t_bonds_etf.index.to_pydatetime()
cad_usd.index = cad_usd.index.to_pydatetime()
tsx_etf.index = tsx_etf.index.to_pydatetime()
nifty_etf.index = nifty_etf.index.to_pydatetime()

# Streamlit app
st.title('Investment Growth Comparison')

# Input for savings account interest rate
interest_rate = st.number_input('Enter the annual interest rate for the savings account (%)', min_value=0.0, value=2.0, step=0.1)

# Asset selection
asset_options = ['S&P 500 Index (VOO)', 'Emerging Market Index (VWO)', '60:40 Split (S&P 500:US T-Bonds)', 'TSX Index Fund (XIU)', 'Nifty Index Fund (INDY)']
selected_asset = st.selectbox('Select the asset to compare against the savings account', asset_options)

# Date range slicer
min_date = s_p500_etf.index.min().date()
max_date = s_p500_etf.index.max().date()
date_range = st.slider('Select date range:', min_value=min_date, max_value=max_date, value=(min_date, max_date), format="MM/YYYY")

start_date, end_date = date_range

# Filter data based on selected date range
s_p500_etf = s_p500_etf[start_date:end_date]
vwo_etf = vwo_etf[start_date:end_date]
t_bonds_etf = t_bonds_etf[start_date:end_date]
cad_usd = cad_usd[start_date:end_date]
tsx_etf = tsx_etf[start_date:end_date]
nifty_etf = nifty_etf[start_date:end_date]

# Reindex ETF data and exchange rates to ensure they match the date range and forward-fill missing data
dates = pd.date_range(start=start_date, end=end_date, freq='MS')
s_p500_etf = s_p500_etf.reindex(dates, method='ffill')
vwo_etf = vwo_etf.reindex(dates, method='ffill')
t_bonds_etf = t_bonds_etf.reindex(dates, method='ffill')
cad_usd = cad_usd.reindex(dates, method='ffill')
tsx_etf = tsx_etf.reindex(dates, method='ffill')
nifty_etf = nifty_etf.reindex(dates, method='ffill')

# Convert ETF prices from USD to CAD
s_p500_etf_cad = s_p500_etf / cad_usd
vwo_etf_cad = vwo_etf / cad_usd
t_bonds_etf_cad = t_bonds_etf / cad_usd
tsx_etf_cad = tsx_etf / cad_usd
nifty_etf_cad = nifty_etf / cad_usd

# Monthly investment
monthly_investment = 1000
months = len(dates)
days_in_month = 30  # Assume each month has 30 days for simplicity
total_days = months * days_in_month

# Checking account (no interest)
checking_account = np.cumsum(np.ones(months) * monthly_investment)

# Savings account with user-defined annual interest rate compounded daily
savings_account = np.zeros(total_days)
daily_interest_rate = (1 + interest_rate / 100) ** (1 / 365) - 1

# Calculate the savings account balance for each day
for day in range(total_days):
    if day == 0:
        savings_account[day] = monthly_investment
    else:
        savings_account[day] = savings_account[day - 1] * (1 + daily_interest_rate)
        # Add the monthly investment at the beginning of each month
        if day % days_in_month == 0:
            savings_account[day] += monthly_investment

# Reshape savings_account to monthly values for plotting
savings_account_monthly = savings_account[::days_in_month]

# Initialize arrays to hold the number of units and portfolio values
s_p500_units = np.zeros(months)
vwo_units = np.zeros(months)
t_bonds_units = np.zeros(months)
tsx_units = np.zeros(months)
nifty_units = np.zeros(months)
s_p500_investment = np.zeros(months)
vwo_investment = np.zeros(months)
t_bonds_investment = np.zeros(months)
tsx_investment = np.zeros(months)
nifty_investment = np.zeros(months)
sixty_forty_units_s = np.zeros(months)
sixty_forty_units_t = np.zeros(months)
sixty_forty_investment = np.zeros(months)

# Purchase ETF units each month and calculate portfolio value
for i in range(months):
    if i == 0:
        s_p500_units[i] = monthly_investment / s_p500_etf_cad.iloc[i]
        vwo_units[i] = monthly_investment / vwo_etf_cad.iloc[i]
        t_bonds_units[i] = monthly_investment / t_bonds_etf_cad.iloc[i]
        tsx_units[i] = monthly_investment / tsx_etf_cad.iloc[i]
        nifty_units[i] = monthly_investment / nifty_etf_cad.iloc[i]
        sixty_forty_units_s[i] = 0.6 * monthly_investment / s_p500_etf_cad.iloc[i]
        sixty_forty_units_t[i] = 0.4 * monthly_investment / t_bonds_etf_cad.iloc[i]
    else:
        s_p500_units[i] = s_p500_units[i-1] + (monthly_investment / s_p500_etf_cad.iloc[i])
        vwo_units[i] = vwo_units[i-1] + (monthly_investment / vwo_etf_cad.iloc[i])
        t_bonds_units[i] = t_bonds_units[i-1] + (monthly_investment / t_bonds_etf_cad.iloc[i])
        tsx_units[i] = tsx_units[i-1] + (monthly_investment / tsx_etf_cad.iloc[i])
        nifty_units[i] = nifty_units[i-1] + (monthly_investment / nifty_etf_cad.iloc[i])
        sixty_forty_units_s[i] = sixty_forty_units_s[i-1] + (0.6 * monthly_investment / s_p500_etf_cad.iloc[i])
        sixty_forty_units_t[i] = sixty_forty_units_t[i-1] + (0.4 * monthly_investment / t_bonds_etf_cad.iloc[i])

    s_p500_investment[i] = s_p500_units[i] * s_p500_etf_cad.iloc[i]
    vwo_investment[i] = vwo_units[i] * vwo_etf_cad.iloc[i]
    t_bonds_investment[i] = t_bonds_units[i] * t_bonds_etf_cad.iloc[i]
    tsx_investment[i] = tsx_units[i] * tsx_etf_cad.iloc[i]
    nifty_investment[i] = nifty_units[i] * nifty_etf_cad.iloc[i]
    sixty_forty_investment[i] = sixty_forty_units_s[i] * s_p500_etf_cad.iloc[i] + sixty_forty_units_t[i] * t_bonds_etf_cad.iloc[i]

# Select the investment based on user choice
if selected_asset == 'S&P 500 Index (VOO)':
    selected_investment = s_p500_investment
elif selected_asset == 'Emerging Market Index (VWO)':
    selected_investment = vwo_investment
elif selected_asset == '60:40 Split (S&P 500:US T-Bonds)':
    selected_investment = sixty_forty_investment
elif selected_asset == 'TSX Index Fund (XIU)':
    selected_investment = tsx_investment
else:
    selected_investment = nifty_investment

# Increase font sizes and adjust the plot for better readability
plt.rcParams.update({
    'font.size': 18,
    'axes.titlesize': 24,
    'axes.labelsize': 20,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 20,
    'figure.titlesize': 28
})

# Function to format y-axis as currency
def currency(x, pos):
    return f'${x:,.0f}'

# Plotting the results
fig, ax = plt.subplots(figsize=(20, 12))

ax.plot(dates, savings_account_monthly, label=f"Savings Account ({interest_rate:.2f}% Annual Interest)")
ax.plot(dates, selected_investment, label=selected_asset)

# Format y-axis as currency
ax.yaxis.set_major_formatter(FuncFormatter(currency))

# Add vertical line segment to highlight the difference
savings_end_value = savings_account_monthly[-1]
investment_end_value = selected_investment[-1]
ax.plot([end_date, end_date], [savings_end_value, investment_end_value], color='gray', linestyle='--', linewidth=2)

# Calculate the difference between savings and investment at the end date
difference = investment_end_value - savings_end_value
difference_text = f'Difference: ${difference:,.0f}'

# Add text annotation (KPI card)
ax.text(end_date, max(investment_end_value, savings_end_value), difference_text,
        horizontalalignment='left', verticalalignment='bottom', fontsize=18, bbox=dict(facecolor='white', alpha=0.8))

ax.set_xlabel("Date")
ax.set_ylabel("Portfolio Value (CAD)")
ax.set_title("Investment Growth Comparison")
legend = ax.legend(prop={'size': 20})  # Explicitly set the legend font size here
ax.grid(True)

st.pyplot(fig)
