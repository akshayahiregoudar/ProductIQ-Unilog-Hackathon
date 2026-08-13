import pandas as pd

expected_file = "data/Unihack_ Expected Output - Delivery Format (1).csv"

expected_df = pd.read_csv(expected_file)

columns = list(expected_df.columns)

print("=" * 60)
print("PRODUCTIQ EXPECTED DELIVERY FORMAT")
print("=" * 60)

print("\nTotal columns:", len(columns))
print("Total template rows:", len(expected_df))

print("\n===== COLUMNS 109 TO 252 =====\n")

for i in range(108, len(columns)):
    print(f"{i + 1} - {columns[i]}")