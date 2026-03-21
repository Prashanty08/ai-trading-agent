uploaded_file = st.file_uploader("Upload Chart Screenshot", type=["png", "jpg", "jpeg"])

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

            st.write(response.output[0].content[0].text)

        else:
            # fallback (no image)
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
