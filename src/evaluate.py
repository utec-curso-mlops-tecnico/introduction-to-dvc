import argparse
import joblib
import pandas as pd
import json
from sklearn.metrics import classification_report
from pathlib import Path

def evaluate(model_path, data_path, out_path):
    model = joblib.load(model_path)
    df = pd.read_csv(data_path)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    preds = model.predict(X)
    report = classification_report(y, preds, output_dict=True)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f)
    print(f"Saved evaluation report to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    evaluate(args.model, args.data, args.out)