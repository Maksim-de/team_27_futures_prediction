import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


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
    data['ticker'] = ticker
    data['asset_name'] = name
    all_data = pd.concat([all_data, data])

for name, ticker in tickers.items():
    download_and_append_data(ticker, name)
    
all_data = all_data.reset_index()

snake_case = {'Open':'open',
              'High':'high',
              'Low':'low',
              'Close':'close',
              'Adj Close':'adj_close',
              'Volume':'volume',
              'Date':'business_date'
}
all_data = all_data.rename(columns=snake_case)

# delete previous data
with engine.connect() as connection:
    connection.execute(text("TRUNCATE TABLE market_data;"))
    
# upload new 
all_data.to_sql(name='market_data', con=engine, if_exists='append', index=False)

print("Historical data loaded into DB")