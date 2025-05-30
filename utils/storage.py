from pathlib import Path
import pandas as pd
import datetime as dt

DATA_FILE = Path("responses.csv")

def store_row(row: dict) -> None:
    """Append one survey result to CSV (UTC timestamp first)."""
    out = {"timestamp": dt.datetime.utcnow().isoformat(timespec="seconds"), **row}
    df = pd.DataFrame([out])
    if DATA_FILE.exists():
        df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")
