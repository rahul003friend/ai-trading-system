if intraday_btn:

    st.subheader("⚡ LIVE INTRADAY BREAKOUT (5 MIN)")

    results = []

    for stock in ALL_STOCKS.keys():

        df = load_intraday(stock)

        if df is None:
            continue

        res = intraday_breakout(df)

        if res is None:
            continue

        signal, entry, sl, target = res

        if signal != "NO TRADE":
            results.append({
                "Stock": stock,
                "Signal": signal,
                "Entry": entry,
                "SL": sl,
                "Target": target
            })

    df_intraday = pd.DataFrame(results)

    if not df_intraday.empty:
        st.dataframe(df_intraday, use_container_width=True)
    else:
        st.warning("No breakout yet")
