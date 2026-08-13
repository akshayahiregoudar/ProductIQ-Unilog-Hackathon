import pandas as pd

# Load dataset
file_path = "data/Unihack_ Sample Dataset - Input.csv"
df = pd.read_csv(file_path)

# Brands we know appear in the dataset
known_brands = [
    "3M",
    "Diablo",
    "DEWALT",
    "Leviton",
    "Satco",
    "Southwire",
    "Milwaukee",
    "Philips",
    "Dremel",
    "Schumacher",
    "Carlon",
    "Irwin",
    "Whirlpool",
    "Frigidaire",
    "Rheem"
]

def detect_brand(description):
    description = str(description).lower()

    for brand in known_brands:
        if brand.lower() in description:
            return brand

    return "Unknown"


df["Detected_Brand"] = df["Part_Desc"].apply(detect_brand)

print("===== BRAND DETECTION RESULTS =====")

print(
    df[
        ["Mfg_Part_Num", "Part_Desc", "Detected_Brand"]
    ].head(20).to_string(index=False)
)

print("\n===== DETECTED BRAND COUNTS =====")

print(df["Detected_Brand"].value_counts())