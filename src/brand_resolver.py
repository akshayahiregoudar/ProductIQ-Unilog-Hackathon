import pandas as pd

# Load dataset
file_path = "data/Unihack_ Sample Dataset - Input.csv"
df = pd.read_csv(file_path)

# Convert placeholder values to missing values
missing_values = [
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --"
]

for value in missing_values:
    df = df.replace(value, pd.NA)


# Brands we can currently recognize from product descriptions
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


def find_brand_in_description(description):
    """Look for a known brand in the product description."""

    text = str(description).lower()

    for brand in known_brands:
        if brand.lower() in text:
            return brand

    return None


def resolve_brand(row):
    """Combine different sources of brand evidence."""

    candidates = []

    # Evidence from existing brand columns
    for column in ["E1_Brand", "Unilog_Brand", "DIB_Brand"]:
        value = row[column]

        if pd.notna(value):
            candidates.append(str(value).strip())

    # Evidence from product description
    description_brand = find_brand_in_description(row["Part_Desc"])

    if description_brand:
        candidates.append(description_brand)

    # No evidence found
    if not candidates:
        return "Unknown", 0.0, "No evidence"

    # Count how many sources support each brand
    counts = {}

    for brand in candidates:
        counts[brand] = counts.get(brand, 0) + 1

    # Select the brand with the most evidence
    best_brand = max(counts, key=counts.get)
    evidence_count = counts[best_brand]

    # Calculate confidence
    if evidence_count >= 2:
        confidence = 0.90
        source = "Multiple sources"
    else:
        confidence = 0.60
        source = "Single source"

    return best_brand, confidence, source


# Run the resolver
results = df.apply(resolve_brand, axis=1)

df["Resolved_Brand"] = results.apply(lambda x: x[0])
df["Brand_Confidence"] = results.apply(lambda x: x[1])
df["Brand_Source"] = results.apply(lambda x: x[2])


# Display results
print("===== BRAND RESOLUTION V2 =====")

print(
    df[
        [
            "Mfg_Part_Num",
            "Part_Desc",
            "E1_Brand",
            "DIB_Brand",
            "Resolved_Brand",
            "Brand_Confidence",
            "Brand_Source"
        ]
    ].head(20).to_string(index=False)
)


print("\n===== BRAND COUNTS =====")
print(df["Resolved_Brand"].value_counts())


print("\n===== CONFIDENCE COUNTS =====")
print(df["Brand_Confidence"].value_counts())
output_file = "output/brand_enriched_products.csv"

df.to_csv(output_file, index=False)

print("\n===== OUTPUT SAVED =====")
print("File:", output_file)