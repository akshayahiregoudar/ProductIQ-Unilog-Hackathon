import pandas as pd
import os

# =========================================================
# FILES
# =========================================================

validated_file = "output/productiq_validated.csv"
template_file = "data/Unihack_ Expected Output - Delivery Format (1).csv"
output_file = "output/ProductIQ_Final_Delivery.csv"

# =========================================================
# LOAD FILES
# =========================================================

validated = pd.read_csv(validated_file)
template = pd.read_csv(template_file)

print("Validated products:", len(validated))
print("Template columns:", len(template.columns))

# Create empty delivery dataframe with same columns
delivery = pd.DataFrame(columns=template.columns)

# Add required rows
delivery = delivery.reindex(range(len(validated)))

# =========================================================
# COPY COMMON FIELDS
# =========================================================

column_map = {
    "Mfg_Part_Num": "Mfg_Part_Num",
    "Part_Desc": "Part_Desc",
    "Part_Manuf": "Part_Manuf",
    "Resolved_Brand": "BRAND_NAME",
    "MANUFACTURER_NAME": "MANUFACTURER_NAME",
    "MANUFACTURER_PART_NUMBER": "MANUFACTURER_PART_NUMBER",
    "Product Name": "Product Name",
    "SHORT_DESC": "SHORT_DESC",
    "LONG_DESC1": "LONG_DESC1",
    "MARKETING_DESCRIPTION": "MARKETING_DESCRIPTION"
}

for source, target in column_map.items():
    if source in validated.columns and target in delivery.columns:
        delivery[target] = validated[source]

# =========================================================
# COPY FEATURE FIELDS
# =========================================================

for i in range(1, 21):

    source = f"ITEM_FEATURES_{i}"

    if source in validated.columns and source in delivery.columns:
        delivery[source] = validated[source]

# =========================================================
# COPY 50 ATTRIBUTE SLOTS
# =========================================================

for i in range(1, 51):

    for field in ["LABEL", "VALUE", "UOM"]:

        source = f"ATTRIBUTE_{field} {i}"
        target = source

        if source in validated.columns and target in delivery.columns:
            delivery[target] = validated[source]

# =========================================================
# ADD VALIDATION INFO
# =========================================================

if "Validation_Status" in validated.columns:
    delivery["TRADE_NAME"] = validated["Validation_Status"]

if "Validation_Score" in validated.columns:
    delivery["Warranty"] = validated["Validation_Score"]

# =========================================================
# DEFAULT VALUES
# =========================================================

defaults = {
    "Country Of Origin": "Unknown",
    "Discontinued": "No",
    "Actual Image (Yes/No)": "No",
    "Selling Qty": 1,
    "Selling UOM": "EA"
}

for column, value in defaults.items():
    if column in delivery.columns:
        delivery[column] = value

# =========================================================
# SAVE
# =========================================================

os.makedirs("output", exist_ok=True)

delivery.to_csv(output_file, index=False)

# =========================================================
# SUMMARY
# =========================================================

filled = delivery.notna().sum().sum()
total = delivery.shape[0] * delivery.shape[1]

print()
print("=" * 60)
print("PRODUCTIQ FINAL DELIVERY GENERATOR")
print("=" * 60)

print("Rows:", len(delivery))
print("Columns:", len(delivery.columns))
print("Filled cells:", filled)
print("Completion:", round(filled / total * 100, 2), "%")

print()
print("Output saved to:")
print(output_file)

print()
print("Hackathon delivery file created successfully! 🚀")