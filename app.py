import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64

# =========================
# DEBUG
# =========================
st.write("App is running...")

# =========================
# LOAD API
# =========================
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

Analyze based on:
- Multi-timeframe alignment
- Market structure
- Support & Resistance
- OI data
- Risk-reward (minimum 1:2)
- Trend + Option context

STRICT RULES:
- No clear setup → NO TRADE
- RR < 1:2 → NO TRADE
- Sideways → NO TRADE

OPTION LOGIC:
- CE → bullish setups
- PE → bearish setups
- Avoid mismatch with trend

PSYCHOLOGY:
- Do not exit early
- Respect stop loss

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

st.title("📊 AI Trading Agent (Multi Chart Fixed)")

symbol = st.text_input("Stock / Index (e.g. RELIANCE.NS or ^NSEI)")

option_type = st.selectbox("Option Type", ["Call (CE)", "Put (PE)"])
strike_price = st.number_input("Strike Price")
entry_price = st.number_input("Option Entry Price")

# =========================
# FETCH DATA
# =========================

data = None
trend = "Unknown"
current_price = None

if symbol:
    data = get_stock_data(symbol)

    if data is not None and not data.empty:
        current_price = data['Close'].iloc[-1]
        trend = get_trend(data)

        st.write(f"📊 Current Price: {current_price}")
        st.write(f"📈 Detected Trend: {trend}")

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

# =========================
# OPTIONAL INPUTS
# =========================

tf_5m = st.text_area("5 min Observation")
tf_15m = st.text_area("15 min Observation")
tf_1h = st.text_area("1H Observation")
tf_daily = st.text_area("Daily Observation")

sr = st.text_area("Support / Resistance")
oi = st.text_area("OI Data")
pos = st.text_area("Your Position")

# =========================
# MULTIPLE IMAGE UPLOAD
# =========================

uploaded_files = st.file_uploader(
    "Upload Multiple Charts (5m / 15m / 1H)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# =========================
# ANALYSIS
# =========================

if st.button("Analyze Trade"):
    try:
        user_input = f"""
        Symbol: {symbol}
        Current Price: {current_price}
        Trend: {trend}

        Option Type: {option_type}
        Strike Price: {strike_price}
        Entry Price: {entry_price}

        5m: {tf_5m}
        15m: {tf_15m}
        1H: {tf_1h}
        Daily: {tf_daily}

        S/R: {sr}
        OI: {oi}
        Position: {pos}
        """

        st.write("Processing...")

        # MULTI IMAGE FIX (BASE64)
        if uploaded_files:
            content = [{"type": "text", "text": SYSTEM_PROMPT + user_input}]

            for file in uploaded_files:
                image_bytes = file.read()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")

                content.append({
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image}"
                })

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "user", "content": content}]
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
