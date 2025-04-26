import yfinance as yf
from supabase import create_client, Client
from datetime import datetime
# from dotenv import load_dotenv
import os


tickers = [
    "^JKSE","ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK",
    "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "CPIN.JK", "CTRA.JK",
    "ESSA.JK", "EXCL.JK", "GOTO.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "ISAT.JK", "ITMG.JK",
    "JPFA.JK", "JSMR.JK", "KLBF.JK", "MAPA.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "PGAS.JK",
    "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SMRA.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
]

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
        today_data["date"] = datetime.now().isoformat()
        del today_data["Dividends"]
        del today_data["Stock Splits"]
   
        today_data["open"] = today_data.pop("Open")
        today_data["high"] = today_data.pop("High")
        today_data["low"] = today_data.pop("Low")
        today_data["close"] = today_data.pop("Close")
        today_data["volume"] = today_data.pop("Volume")

        today_data["created_at"] = datetime.now().isoformat()

        allData.append(today_data)
    else:
        print(f"No data available for {ticker}")



#if remote

url : str = os.environ["DB_URL"]
key : str = os.environ["DB_KEY"]

# if local
# load_dotenv()
# url: str = os.getenv("DB_URL")
# key: str = os.getenv("DB_KEY")

supabase = create_client(url, key)
response = (
    supabase.table("StockData")
    .insert(allData)
    .execute()
)
print(response)
