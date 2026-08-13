import pandas as pd

file_path = "data/Unihack_ Sample Dataset - Input.csv"

df = pd.read_csv(file_path)

print("===== DATASET OVERVIEW =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DUPLICATE ROWS =====")
print("Duplicate rows:", df.duplicated().sum())

print("\n===== UNIQUE VALUES =====")
print("Unique part numbers:", df["Mfg_Part_Num"].nunique())
print("Unique E1 brands:", df["E1_Brand"].nunique())
print("Unique Unilog brands:", df["Unilog_Brand"].nunique())
print("Unique DIB brands:", df["DIB_Brand"].nunique())
print("Unique manufacturers:", df["Part_Manuf"].nunique())

print("\n===== SAMPLE PRODUCTS =====")
print(df[[
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf"
]].head(10).to_string(index=False))