import os
import numpy as np
from SupabaseManager import get_supabase_client
from datetime import date

isProd = True
supabase = get_supabase_client(isProd= isProd)

def fetch_data_for_date(supabase, date: str):
    result = supabase.rpc("fetch_price_accuracy_stat", {"target_date": date}).execute()

    return result.data

if __name__ == "__main__":
    # curr_date = date.today()
    curr_date = "2025-9-26"
    formatted_date = curr_date.strftime("%Y-%m-%d")
    data = fetch_data_for_date(supabase, formatted_date)
    
    tickers = []
    newAccuracies = []
    for record in data:
        ticker = record['ticker']
        actual_price = record['actual_price']
        predicted_price = record['predicted_price']
        accuracy = record['accuracy']
        n_inference = record['n_inference']

        todayAccuracy = (1 - abs(actual_price - predicted_price) / actual_price)

        newAccuracy = 0
        if n_inference > 1:
            newAccuracy = (accuracy * n_inference + todayAccuracy) / (n_inference + 1)
        else:
            newAccuracy = todayAccuracy
        
        tickers.append(ticker)
        newAccuracies.append(newAccuracy)

    res = supabase.rpc("update_stock_accuracy", {
        "tickers": tickers,
        "accuracies": newAccuracies
    }).execute()

    print(res)

