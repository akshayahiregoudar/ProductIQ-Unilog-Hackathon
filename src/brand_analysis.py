import pandas as pd

file_path = "data/Unihack_ Sample Dataset - Input.csv"

df = pd.read_csv(file_path)

print("===== E1 BRANDS =====")
print(df["E1_Brand"].value_counts())

print("\n===== UNILOG BRANDS =====")
print(df["Unilog_Brand"].value_counts())

print("\n===== DIB BRANDS =====")
print(df["DIB_Brand"].value_counts())