import streamlit as st
from openai import OpenAI

# Debug line
st.write("App is running...")

# Load API
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"API Key Error: {e}")

# Prompt
SYSTEM_PROMPT = """
You are an elite options trader and strict trading coach.

Your job is NOT to predict market but to enforce discipline and high-quality trades.

Analyze based on:
1. Multi-timeframe alignment (5m, 15m, 1H, Daily)
2. Market structure (trend, HH/HL, LH/LL)
3. Support & Resistance
4. OI data (smart money behavior)
5. Risk-reward (minimum 1:2)

STRICT RULES:
- If timeframes are not aligned → NO TRADE
- If RR < 1:2 → NO TRADE
- If market is sideways → NO TRADE
- Do not force setups

SPECIAL FOCUS (Trader Psychology):
- Trader tends to exit early in profit → encourage holding winners
- Trader holds losing trades → enforce strict SL discipline

Output format:

Bias: (Bullish / Bearish / Neutral)

Trade Decision:
(Trade / No Trade)

Entry:
Stop Loss:
Target:

Confidence: (1-10)

Reason:
- Clear logic

Psychology Instruction:
- What trader should DO right now
- What trader should NOT do
"""

# UI
st.title("📊 AI Trading Agent")

symbol = st.text_input("Stock / Index")

tf_5m = st.text_area("5 min")
tf_15m = st.text_area("15 min")
tf_1h = st.text_area("1H")
tf_daily = st.text_area("Daily")

sr = st.text_area("Support/Resistance")
oi = st.text_area("OI Data")
pos = st.text_area("Your Position")

# Button
if st.button("Analyze"):
    try:
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

        st.write("Processing...")

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
