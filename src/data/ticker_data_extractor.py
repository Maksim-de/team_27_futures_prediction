import yfinance as yf
import pandas as pd
from datetime import datetime

tickers = {
    "WTI": "CL=F",        # WTI Crude Oil
    "BRENT": "BZ=F",      # Brent Crude Oil
    "S&P 500": "SPY",     # SPDR S&P 500 ETF Trust (replaces ^GSPC). Using tickers that are traded
    "Nasdaq-100": "QQQ"   # Invesco QQQ Trust (replaces ^NDX)
}


start_date = "2022-01-01"
end_date = datetime.now().strftime('%Y-%m-%d')

def download_and_save_data(ticker, name):
    data = yf.download(ticker, start=start_date, end=end_date)
    file_name = f"{name}_data.csv"
    data.to_csv(file_name)
    print(f"Data for {name} saved into {file_name}")

for name, ticker in tickers.items():
    download_and_save_data(ticker, name)

print("Historical data loaded")
