import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a professional options trader and trading psychology coach.

Analyze based on:
1. Multi-timeframe trend alignment
2. Market structure
3. Support & Resistance
4. OI data interpretation
5. Risk-reward (minimum 1:2)

Rules:
- If no clear setup → NO TRADE
- Do not force trades
- Focus on discipline

Output:

Bias:
Trade Setup:
Entry:
Stop Loss:
Target:
Confidence:
Reason:
Psychology Advice:
"""

st.title("📊 AI Trading Agent")

symbol = st.text_input("Stock / Index")

tf_5m = st.text_area("5 min")
tf_15m = st.text_area("15 min")
tf_1h = st.text_area("1H")
tf_daily = st.text_area("Daily")

sr = st.text_area("Support/Resistance")
oi = st.text_area("OI Data")
pos = st.text_area("Your Position")

if st.button("Analyze"):

    user_input = f"""
    Symbol: {symbol}

    5m: {tf_5m}
    15m: {tf_15m}
    1H: {tf_1h}
    Daily: {tf_daily}

    S/R: {sr}
    OI: {oi}
    Position: {pos}
    """

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    st.write(response.choices[0].message.content)
