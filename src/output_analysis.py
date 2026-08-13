import pandas as pd

file_path = "data/Unihack_ Expected Output - Delivery Format (1).csv"

df = pd.read_csv(file_path)

print("===== EXPECTED OUTPUT =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== ALL COLUMN NAMES =====")

for number, column in enumerate(df.columns, start=1):
    print(number, ":", column)

print("\n===== FIRST 5 ROWS =====")
print(df.head().to_string())