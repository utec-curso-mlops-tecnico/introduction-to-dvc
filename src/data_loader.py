import pandas as pd

def load_csv(path):
    """Carga CSV y devuelve DataFrame."""
    return pd.read_csv(path)

if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "data/in/application_data.csv"
    df = load_csv(p)
    print(f"Loaded {len(df)} rows from {p}")