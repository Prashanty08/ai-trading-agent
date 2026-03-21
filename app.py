import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Debug
st.write("App is running...")

# Load API key
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"API Key Error: {e}")

# =========================
# DATA FUNCTIONS
# =========================

def get_stock_data(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="5m")
        return data
    except:
        return None

def get_trend(data):
    try:
        if data['Close'].iloc[-1] > data['Close'].mean():
            return "Bullish"
        else:
            return "Bearish"
    except:
        return "Unknown"

# =========================
# AI PROMPT
# =========================

SYSTEM_PROMPT = """
You are an elite options trader and strict trading coach.

Your job is NOT to predict market but to enforce discipline and high-quality trades.

Analyze based on:
1. Multi-timeframe alignment
2. Market structure
3. Support & Resistance
4. OI data (smart money behavior)
5. Risk-reward (minimum 1:2)
6. System detected trend

STRICT RULES:
- If no clear setup → NO TRADE
- If RR < 1:2 → NO TRADE
- If market is sideways → NO TRADE

PSYCHOLOGY RULES:
- Do not allow early exit in profit
- Enforce strict stop loss

Output:

Bias:
Trade Decision:
Entry:
Stop Loss:
Target:
Confidence:

Reason:

Psychology Instruction:
- What to DO
- What NOT to do
"""

# =========================
# UI
# =========================

st.title("📊 AI Trading Agent (Auto Data Version)")

symbol = st.text_input("Stock / Index (e.g. RELIANCE.NS or ^NSEI)")
entry_price = st.number_input("Option Entry Price")

# Fetch data
data = None
trend = "Unknown"

if symbol:
    data = get_stock_data(symbol)

    if data is not None and not data.empty:
        latest_price = data['Close'].iloc[-1]
        trend = get_trend(data)

        st.write(f"📊 Current Price: {latest_price}")
        st.write(f"📈 Detected Trend: {trend}")

        # Chart
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

# Manual inputs (optional but powerful)
tf_5m = st.text_area("5 min Observation")
tf_15m = st.text_area("15 min Observation")
tf_1h = st.text_area("1H Observation")
tf_daily = st.text_area("Daily Observation")

sr = st.text_area("Support / Resistance")
oi = st.text_area("OI Data")
pos = st.text_area("Your Position")

# Upload chart
uploaded_file = st.file_uploader("Upload Chart Screenshot", type=["png", "jpg", "jpeg"])

# =========================
# ANALYSIS BUTTON
# =========================

if st.button("Analyze Trade"):
    try:
        user_input = f"""
        Symbol: {symbol}
        Entry Price: {entry_price}
        Detected Trend: {trend}

        5m: {tf_5m}
        15m: {tf_15m}
        1H: {tf_1h}
        Daily: {tf_daily}

        Support/Resistance: {sr}
        OI Data: {oi}
        Position: {pos}
        """

        st.write("Processing...")

        # If image uploaded
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": SYSTEM_PROMPT + user_input},
                            {"type": "input_image", "image_bytes": image_bytes}
                        ]
                    }
                ]
            )

            st.success("Analysis Complete")
            st.write(response.output[0].content[0].text)

        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ]
            )

            st.success("Analysis Complete")
            st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error: {e}")
