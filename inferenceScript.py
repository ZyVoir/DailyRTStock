import os
import numpy as np
import pandas as pd
import joblib
from datetime import timedelta
from keras.models import load_model
from supabase import create_client, Client

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
    """
    Load the latest 15 closing prices for each ticker from Supabase
    
    Args:
        supabase: Supabase client
        tickers: List of ticker symbols
    
    Returns:
        dict: Dictionary with ticker as key and DataFrame as value
    """
    all_ticker_data = {}
    
    for ticker in tickers:
        try:
            # Query the latest 15 records for each ticker, ordered by date descending
            response = supabase.table("StockData") \
                .select("*") \
                .eq("Ticker", ticker) \
                .order("Date", desc=True) \
                .limit(15) \
                .execute()
            
            if response.data:
                # Convert to DataFrame and reverse to get chronological order
                df = pd.DataFrame(response.data)
                df = df.sort_values('Date').reset_index(drop=True)
                df['Date'] = pd.to_datetime(df['Date'])
                all_ticker_data[ticker] = df
                print(f"Loaded {len(df)} records for {ticker}")
            else:
                print(f"No data found for {ticker}")
                
        except Exception as e:
            print(f"Error loading data for {ticker}: {str(e)}")
            continue
    
    return all_ticker_data

def forecast_lstm(model, ticker, scaler, recent_data, seq_len=15, steps=1):
    """
    Forecasting function for a specific ticker
    
    Args:
        model: Loaded LSTM model
        ticker: Stock ticker symbol
        scaler: Loaded scaler for the specific ticker
        recent_data: Recent stock data (should contain ['Open', 'High', 'Low', 'Close'])
        seq_len: Sequence length for LSTM input (default: 15)
        steps: Number of prediction steps (default: 1)
    
    Returns:
        predictions: List of predicted prices
        prediction_dates: List of prediction dates
    """
    
    # Extract OHLC data
    ohlc_data = recent_data[['Open', 'High', 'Low', 'Close']].values[-(seq_len + steps - 1):]
    
    if len(ohlc_data) < seq_len + steps - 1:
        raise ValueError(f"Insufficient data for forecasting {ticker}. Need at least {seq_len + steps - 1} rows.")
    
    predictions = []
    prediction_dates = []
    last_date = recent_data['Date'].iloc[-1]
    
    for i in range(steps):
        start = i
        end = i + seq_len
        input_seq = ohlc_data[start:end]
        
        # Scale the input
        scaled_input = scaler.transform(input_seq)
        model_input = scaled_input.reshape(1, seq_len, 4)
        
        # Make prediction
        pred_scaled = model.predict(model_input, verbose=0)
        
        # Inverse transform to get actual price
        dummy = np.hstack([np.zeros((1, 3)), pred_scaled])
        pred_unscaled = scaler.inverse_transform(dummy)[0, 3]
        
        predictions.append(pred_unscaled)
        pred_date = last_date + timedelta(days=i + 1)
        prediction_dates.append(pred_date)
    
    return predictions, prediction_dates

def run_inference():
    """
    Main inference function that processes all tickers
    """
    all_results = {}
    url: str = os.environ["DB_URL"]
    key: str = os.environ["DB_KEY"]
    
    # Establish connection to Supabase
    supabase: Client = create_client(url, key)
    
    # Load data from Supabase
    df_all = load_data_from_supabase(supabase, tickers)

    for ticker in tickers:
        try:
            # Load scaler for the specific ticker
            scaler = joblib.load(os.path.join('scalers', f"{ticker}.pkl"))
            
            # Filter data for current ticker from Supabase data
            if ticker in df_all:
                recent_data = df_all[ticker]
                
                # Make predictions
                predictions, prediction_dates = forecast_lstm(model, ticker, scaler, recent_data)
                
                # Store results
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
    
    #TODO: Post results to Supabase
    # post_results_to_supabase(all_results)
    
    return all_results

if __name__ == "__main__":
    results = run_inference()