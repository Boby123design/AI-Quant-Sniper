import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import joblib
import time
import winsound  # Windows ka in-built Alarm Sound 🔔

# ==========================================
# 1. UI SETUP
# ==========================================
st.set_page_config(page_title="AI Quant Sniper", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00e676;'>🎯 AI Quant Sniper Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 2. LOAD MODEL & MT5
# ==========================================
@st.cache_resource
def load_brain():
    try:
        return joblib.load("trained.pkl")
    except:
        return None

model = load_brain()

if model is None:
    st.error("🚨 'trained.pkl' nahi mili! Pehle AI ko train karein.")
    st.stop()

if not mt5.initialize():
    st.error("🚨 MT5 se connect nahi ho pa raha! MT5 open rakhein.")
    st.stop()

symbol = "BTCUSDT"
threshold = 60.0  # 60% Confidence Rule

# ==========================================
# 3. LIVE SCANNER ENGINE
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 START LIVE SCANNER", use_container_width=True):
        st.success(f"📡 AI Scanner is LIVE for {symbol}...")
        
        # Ek khali dabba (box) jisme data update hota rahega bina page refresh kiye
        ui_box = st.empty()

        while True:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 30)
            if rates is not None:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.rename(columns={'tick_volume': 'volume'}, inplace=True)
                
                # Math Calculations
                delta = df['close'].diff()
                gain = delta.where(delta > 0, 0.0)
                loss = -delta.where(delta < 0, 0.0)
                avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
                avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
                rs = avg_gain / avg_loss
                df['RSI_14'] = 100 - (100 / (1 + rs))
                
                df['Candle_Size'] = df['high'] - df['low']
                df['Body_Size'] = df['close'] - df['open']
                df['Wick_Top'] = df['high'] - df[['open', 'close']].max(axis=1)
                df['Wick_Bottom'] = df[['open', 'close']].min(axis=1) - df['low']
                
                df.dropna(inplace=True)
                current_candle = df.iloc[-1]
                
                features = ['volume', 'RSI_14', 'Candle_Size', 'Body_Size', 'Wick_Top', 'Wick_Bottom']
                X_live = pd.DataFrame([current_candle[features]])
                
                # AI Prediction
                probs = model.predict_proba(X_live)[0]
                prob_sell = probs[0] * 100
                prob_buy = probs[1] * 100
                
                price = current_candle['close']
                
                # --- UI UPDATE & NOTIFICATION ALARM ---
                with ui_box.container():
                    if prob_buy > threshold:
                        st.markdown(f"<div style='background-color: #00c853; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0px 0px 20px #00c853;'><h1 style='color: white;'>🟢 STRONG BUY SETUP!</h1><h2>Price: {price} | AI Confidence: {prob_buy:.1f}%</h2></div>", unsafe_allow_html=True)
                        winsound.Beep(1000, 1000) # (Frequency: High, Duration: 1 second)
                        
                    elif prob_sell > threshold:
                        st.markdown(f"<div style='background-color: #d50000; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0px 0px 20px #d50000;'><h1 style='color: white;'>🔴 STRONG SELL SETUP!</h1><h2>Price: {price} | AI Confidence: {prob_sell:.1f}%</h2></div>", unsafe_allow_html=True)
                        winsound.Beep(500, 1000)  # (Frequency: Low, Duration: 1 second)
                        
                    else:
                        st.markdown(f"<div style='background-color: #1e1e1e; padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #444;'><h2 style='color: #a0a0a0;'>⏳ Waiting for Liquidity Sweep... (No Trade)</h2><p style='font-size: 18px;'>Current Price: {price}<br>Buy Prob: {prob_buy:.1f}% | Sell Prob: {prob_sell:.1f}%</p></div>", unsafe_allow_html=True)
            
            # Har 3 second mein market check karega
            time.sleep(3)
        