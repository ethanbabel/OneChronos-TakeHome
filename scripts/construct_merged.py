import pandas as pd

def construct_merged_dataset(
    trades: pd.DataFrame, quotes: pd.DataFrame
) -> pd.DataFrame:
    trades = trades.copy()
    quotes = quotes.copy()

    trades["transaction_timestamp"] = pd.to_datetime(trades["transaction_timestamp"])
    quotes["transaction_timestamp"] = pd.to_datetime(quotes["transaction_timestamp"])

    trades = trades.sort_values(["transaction_timestamp", "symbol_id"])
    quotes = quotes.sort_values(["transaction_timestamp", "symbol_id"])

    merged = pd.merge_asof(
        trades,
        quotes,
        on="transaction_timestamp",
        by="symbol_id",
        direction="backward",
        suffixes=("_trade", "_quote"),
    )

    if "price_decimal_trade" in merged.columns and "price_decimal_quote" in merged.columns:
        merged["price_decimal"] = merged["price_decimal_trade"].combine_first(
            merged["price_decimal_quote"]
        )
        merged = merged.drop(columns=["price_decimal_trade", "price_decimal_quote"])

    merged = merged.rename(
        columns={
            "bid_price": "NBBO_bid_price",
            "bid_size": "NBBO_bid_size",
            "ask_price": "NBBO_ask_price",
            "ask_size": "NBBO_ask_size",
        }
    )

    return merged

def main() -> None:
    trades_path = "data/trade_data_2024_04_01.csv"
    quotes_path = "data/quote_data_2024_04_01.csv"
    output_path = "data/merged_trade_quote_2024_04_01.csv"

    trades = pd.read_csv(trades_path)
    quotes = pd.read_csv(quotes_path)

    merged = construct_merged_dataset(trades, quotes)
    merged.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
