import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

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

Your job is NOT to predict market but to enforce discipline and high-quality trades.

Analyze based on:
1. Multi-timeframe alignment
2. Market structure
3. Support & Resistance
4. OI data (smart money behavior)
5. Risk-reward (minimum 1:2)
6. System detected trend
7. Option context (Call/Put + Strike relevance)

STRICT RULES:
- If no clear setup → NO TRADE
- If RR < 1:2 → NO TRADE
- If market is sideways → NO TRADE

OPTION LOGIC:
- Call (CE) → prefer bullish setups
- Put (PE) → prefer bearish setups
- Avoid trades where option contradicts trend
- Consider if strike is ITM / ATM / OTM

PSYCHOLOGY RULES:
- Do not exit early in profit
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

st.title("📊 AI Trading Agent (Option Smart Version)")

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
# IMAGE UPLOAD
# =========================

uploaded_file = st.file_uploader("Upload Chart Screenshot", type=["png", "jpg", "jpeg"])

# =========================
# ANALYSIS
# =========================

if st.button("Analyze Trade"):
    try:
        user_input = f"""
        Symbol: {symbol}
        Current Price: {current_price}
        Detected Trend: {trend}

        Option Type: {option_type}
        Strike Price: {strike_price}
        Entry Price: {entry_price}

        5m: {tf_5m}
        15m: {tf_15m}
        1H: {tf_1h}
        Daily: {tf_daily}

        Support/Resistance: {sr}
        OI Data: {oi}
        Position: {pos}
        """

        st.write("Processing...")

        # WITH IMAGE
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
            # WITHOUT IMAGE
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
