import yfinance as yf
from datetime import datetime, date
import os
from SupabaseManager import get_supabase_client


tickers = [
    "^JKSE","ACES.JK", "ADMR.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK",
    "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK",
    "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK",
    "BRPT.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK",
    "GOTO.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK",
    "ISAT.JK", "ITMG.JK", "JPFA.JK", "JSMR.JK", "KLBF.JK",
    "MAPA.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK",
    "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK",
    "SMRA.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK"
]



start_date = "2025-01-01"

curr_date = date.today()
formatted_date = curr_date.strftime("%Y-%m-%d")
end_date = formatted_date

allData = []

for ticker in tickers:
    tickerData = yf.Ticker(ticker)
    tickerData = tickerData.history(start=start_date, end=end_date, auto_adjust=False)
    tickerData.reset_index(inplace=True)

    if not tickerData.empty:
        for index, row in tickerData.iterrows():
            data_dict = row.to_dict()
            data_dict["ticker"] = ticker
            data_dict["date"] = data_dict["Date"].isoformat()
            del data_dict["Date"]
            del data_dict["Dividends"]
            del data_dict["Stock Splits"]
            data_dict.pop("Adj Close", None)

            data_dict["open"] = data_dict.pop("Open")
            data_dict["high"] = data_dict.pop("High")
            data_dict["low"] = data_dict.pop("Low")
            data_dict["close"] = data_dict.pop("Close")
            data_dict["volume"] = data_dict.pop("Volume")

            data_dict["created_at"] = datetime.now().isoformat()

            allData.append(data_dict)
    else:
        print(f"No data available for {ticker}")

print(allData)

isProd = True
supabase = get_supabase_client(isProd= isProd)
response = (
    supabase.table("StockData")
    .insert(allData)
    .execute()
)
