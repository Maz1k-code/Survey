from pathlib import Path
import pandas as pd
import datetime as dt

DATA_FILE = Path("responses.csv")

def store_row(row: dict) -> None:
    """Persist one full survey to CSV (UTC timestamp)."""
    out = {
        "timestamp": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "name": row.get("name"),
        "city": row.get("city"),
        "one_liner": row.get("one_liner"),
        "metrics": row.get("metrics"),
        "funding": row.get("funding"),
        "video_file_id": row.get("video_file_id"),
        # join multiple media IDs by ‘|’
        "media_file_ids": "|".join(row.get("media", []))
    }
    df = pd.DataFrame([out])
    if DATA_FILE.exists():
        df.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")
