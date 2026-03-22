import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64

st.write("App is running...")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"API Key Error: {e}")

# =========================
# FUNCTIONS
# =========================

def get_stock_data(symbol):
    try:
        return yf.download(symbol, period="5d", interval="5m")
    except:
        return None

def get_trend(data):
    try:
        return "Bullish" if data['Close'].iloc[-1] > data['Close'].mean() else "Bearish"
    except:
        return "Unknown"

def classify_option(current_price, strike_price, option_type):
    try:
        diff = current_price - strike_price

        if abs(diff) < 50:
            return "ATM"

        if option_type == "Call (CE)":
            return "ITM" if current_price > strike_price else "OTM"

        if option_type == "Put (PE)":
            return "ITM" if current_price < strike_price else "OTM"

    except:
        return "Unknown"

# =========================
# PROMPT
# =========================

SYSTEM_PROMPT = """
You are an elite options trader.

STRICT RULES:
- No alignment → NO TRADE
- RR < 1:2 → NO TRADE

OPTION LOGIC:
- CE → bullish only
- PE → bearish only
- Avoid OTM unless breakout
- Prefer ATM/ITM

PSYCHOLOGY:
- Hold winners
- Cut losers strictly

Output:

Bias:
Trade Decision:
Entry:
Stop Loss:
Target:
Confidence:

Reason:

Psychology Instruction:
"""

# =========================
# UI
# =========================

st.title("📊 AI Trading Agent (Smart Automation)")

symbol = st.text_input("Stock / Index (e.g. RELIANCE.NS or ^NSEI)")
option_type = st.selectbox("Option Type", ["Call (CE)", "Put (PE)"])
strike_price = st.number_input("Strike Price")
entry_price = st.number_input("Option Entry Price")

data = None
trend = "Unknown"
current_price = None
option_position = "Unknown"

if symbol:
    data = get_stock_data(symbol)

    if data is not None and not data.empty:
        current_price = data['Close'].iloc[-1]
        trend = get_trend(data)
        option_position = classify_option(current_price, strike_price, option_type)

        st.write(f"📊 Current Price: {current_price}")
        st.write(f"📈 Trend: {trend}")
        st.write(f"🎯 Option Type: {option_position}")

        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close']
            )
        ])

        st.plotly_chart(fig, use_container_width=True)

# Inputs
tf_5m = st.text_area("5m")
tf_15m = st.text_area("15m")
tf_1h = st.text_area("1H")
tf_daily = st.text_area("Daily")
sr = st.text_area("S/R")
oi = st.text_area("OI")
pos = st.text_area("Position")

uploaded_files = st.file_uploader(
    "Upload Charts",
    type=["png", "jpg"],
    accept_multiple_files=True
)

# =========================
# ANALYSIS
# =========================

if st.button("Analyze"):
    try:
        user_input = f"""
        Symbol: {symbol}
        Price: {current_price}
        Trend: {trend}

        Option: {option_type}
        Strike: {strike_price}
        Entry: {entry_price}
        Position Type: {option_position}

        5m: {tf_5m}
        15m: {tf_15m}
        1H: {tf_1h}
        Daily: {tf_daily}

        S/R: {sr}
        OI: {oi}
        Position: {pos}
        """

        st.write("Processing...")

        if uploaded_files:
            content = [{"type": "input_text", "text": SYSTEM_PROMPT + user_input}]

            for file in uploaded_files:
                img = base64.b64encode(file.read()).decode("utf-8")
                content.append({
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{img}"
                })

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "user", "content": content}]
            )

            st.write(response.output[0].content[0].text)

        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]
            )

            st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error: {e}")
