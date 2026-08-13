import pandas as pd

# Load the input dataset
file_path = "data/Unihack_ Sample Dataset - Input.csv"
df = pd.read_csv(file_path)

print("Before cleaning:")
print(df.head(3).to_string(index=False))

# Values that mean "information is not available"
missing_values = [
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --"
]

# Replace those values with proper missing values
for value in missing_values:
    df = df.replace(value, pd.NA)

print("\nAfter cleaning:")
print(df.head(3).to_string(index=False))

print("\nMissing values after cleaning:")
print(df.isna().sum())