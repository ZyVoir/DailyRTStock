import os
import numpy as np
import pandas as pd
import joblib
from datetime import timedelta, datetime
from keras.models import load_model
import SupabaseManager

import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

isProd = True
supabase = SupabaseManager.get_supabase_client(isProd = isProd)

# Load LSTM model
model = load_model('model/LSTM.h5')

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

def load_data_from_supabase(supabase: Client, tickers: list):
    
    all_ticker_data = {}
    
    for ticker in tickers:
        try:
            # Query the latest 20 records for each ticker, ordered by date descending
            response = supabase.table("StockData") \
                .select("*") \
                .eq("ticker", ticker) \
                .order("date", desc=True) \
                .limit(20) \
                .execute()
            
            if response.data:
                # Convert to DataFrame and reverse to get chronological order
                df = pd.DataFrame(response.data)
                df = df.sort_values('date').reset_index(drop=True)
                df['date'] = pd.to_datetime(df['date'])
                all_ticker_data[ticker] = df
                print(f"Loaded {len(df)} records for {ticker}")
            else:
                print(f"No data found for {ticker}")
                
        except Exception as e:
            print(f"Error loading data for {ticker}: {str(e)}")
            continue
    
    return all_ticker_data

def forecast_lstm(model, ticker, scaler, recent_data, seq_len=15, steps=5):
    
    ohlc_data = recent_data[['open', 'high', 'low', 'close']].values
    
    if len(ohlc_data) < seq_len + steps:
        raise ValueError(f"Insufficient data for forecasting {ticker}")
    
    predictions = []
    prediction_dates = []
    last_date = recent_data['date'].iloc[-1]
    
    for i in range(steps):
        start = i
        end = i + seq_len
        input_seq = ohlc_data[start:end]
        
        scaled_input = scaler.transform(input_seq)
        model_input = scaled_input.reshape(1, seq_len, 4)
        
        pred_scaled = model.predict(model_input, verbose=0)
        
        dummy = np.hstack([np.zeros((1, 3)), pred_scaled])
        pred_unscaled = scaler.inverse_transform(dummy)[0, 3]
        
        predictions.append(pred_unscaled)
        pred_date = last_date + timedelta(days=i + 1)
        prediction_dates.append(pred_date)
    
    return predictions, prediction_dates

def clean_results(all_results):

    cleaned_records = []
    
    for ticker, data in all_results.items():
        predictions = data['predictions']
        dates = data['dates']
        
        for i, (prediction, date) in enumerate(zip(predictions, dates)):
            record = {
                'ticker': ticker,
                'date': date.strftime('%Y-%m-%d'),  
                'closePrediction': float(prediction),  
                'created_at': datetime.now().isoformat()  
            }
            cleaned_records.append(record)
    
    return cleaned_records

def post_results_to_supabase(all_results):

    try:
        response = supabase.table("StockPrediction").insert(all_results).execute()
        
        if response.data:
            print(f"Successfully inserted {len(all_results)} prediction records to Supabase")
        else:
            print("Failed to insert records to Supabase")
            
    except Exception as e:
        print(f"Error posting results to Supabase: {str(e)}")

def run_inference():
    
    all_results = {}
   
    
    df_all = load_data_from_supabase(supabase, tickers)
    

    for ticker in tickers:
        try:
            scaler = joblib.load(os.path.join('scalers', f"{ticker}.pkl"))
            
            if ticker in df_all:
                recent_data = df_all[ticker]
                predictions, prediction_dates = forecast_lstm(model, ticker, scaler, recent_data)
                
                all_results[ticker] = {
                    'predictions': predictions,
                    'dates': prediction_dates
                }
                
                print(f"Predictions generated for {ticker}")
            else:
                print(f"No data available for {ticker}")
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            continue
    
    return all_results

if __name__ == "__main__":
    results = run_inference()
    cleaned_results = clean_results(results)
    # print(cleaned_results)
    post_results_to_supabase(cleaned_results)