import argparse
import pandas as pd
from pathlib import Path

def prepare(input_path, output_path):
    df = pd.read_csv(input_path)
    # Limpieza mínima: eliminar filas con NA
    df = df.dropna()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    prepare(args.input, args.output)