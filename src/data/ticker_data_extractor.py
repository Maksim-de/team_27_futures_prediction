import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME')
}


db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)


tickers = {
    "WTI": "CL=F",        # WTI Crude Oil
    "BRENT": "BZ=F",      # Brent Crude Oil
    "S&P 500": "SPY",     # SPDR S&P 500 ETF Trust (replaces ^GSPC). Using tickers that are traded
    "Nasdaq-100": "QQQ"   # Invesco QQQ Trust (replaces ^NDX)
}

start_date = "2022-01-01"
end_date = datetime.now().strftime('%Y-%m-%d')

all_data = pd.DataFrame()

def download_and_append_data(ticker, name):
    global all_data
    
    data = yf.download(ticker, start=start_date, end=end_date)    
    data['Ticker'] = name
    
    all_data = pd.concat([all_data, data])

for name, ticker in tickers.items():
    download_and_append_data(ticker, name)

# uploading
all_data.to_sql(name='market_data', con=engine, if_exists='replace', index=False)

print("Historical data loaded into DB")
all_data