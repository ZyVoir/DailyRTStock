import yfinance as yf
from datetime import datetime, timedelta
import os
from SupabaseManager import get_supabase_client, get_ticker_list

tickers = get_ticker_list()

period = "1d"
interval = "1d"

allData = []

for ticker in tickers:
    tickerData = yf.Ticker(ticker)
    tickerData = tickerData.history(period=period, interval=interval, auto_adjust=False)
    tickerData.reset_index(inplace=True)

    if not tickerData.empty:
        today_data = tickerData.iloc[-1].to_dict()
        del today_data["Date"]
        today_data["ticker"] = ticker
        # today_data["date"] = datetime.now().isoformat()
        today_data["date"] = (datetime.now() - timedelta(days=1)).isoformat()
        del today_data["Dividends"]
        del today_data["Stock Splits"]
        
        today_data.pop("Adj Close", None)

        today_data["open"] = today_data.pop("Open")
        today_data["high"] = today_data.pop("High")
        today_data["low"] = today_data.pop("Low")
        today_data["close"] = today_data.pop("Close")
        today_data["volume"] = today_data.pop("Volume")

        today_data["created_at"] = datetime.now().isoformat()

        allData.append(today_data)
    else:
        print(f"No data available for {ticker}")

isProd = True
supabase = get_supabase_client(isProd = isProd) 
response = (
    supabase.table("StockData")
    .insert(allData)
    .execute()
)
