import pandas as pd
import re
import os


# =========================================================
# 1. FILE PATHS
# =========================================================

input_file = "output/productiq_enriched_products.csv"
output_file = "output/productiq_content_enriched.csv"


# =========================================================
# 2. LOAD ENRICHED DATA
# =========================================================

df = pd.read_csv(input_file)

print("Enriched dataset loaded!")
print("Rows:", len(df))


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def clean_text(value):
    """Clean empty/NaN values."""

    if pd.isna(value):
        return ""

    return str(value).strip()


def get_attributes(row):
    """Read the 50 attribute slots."""

    attributes = []

    for i in range(1, 51):

        label = clean_text(
            row.get(
                f"ATTRIBUTE_LABEL {i}",
                ""
            )
        )

        value = clean_text(
            row.get(
                f"ATTRIBUTE_VALUE {i}",
                ""
            )
        )

        uom = clean_text(
            row.get(
                f"ATTRIBUTE_UOM {i}",
                ""
            )
        )

        if label and value:

            if uom:
                text = f"{label}: {value} {uom}"
            else:
                text = f"{label}: {value}"

            attributes.append(text)

    return attributes


# =========================================================
# 4. GENERATE PRODUCT NAME
# =========================================================

def generate_product_name(row):

    description = clean_text(
        row.get("Part_Desc", "")
    )

    brand = clean_text(
        row.get("Resolved_Brand", "")
    )

    part_number = clean_text(
        row.get("Mfg_Part_Num", "")
    )

    # Remove duplicate part number from description
    product_text = description

    if part_number:

        product_text = re.sub(
            re.escape(part_number),
            "",
            product_text,
            flags=re.IGNORECASE
        ).strip()

    # Avoid Unknown as a brand
    if brand and brand != "Unknown":

        if brand.lower() not in product_text.lower():

            product_text = (
                f"{brand} {product_text}"
            )

    return product_text.strip()


# =========================================================
# 5. GENERATE SHORT DESCRIPTION
# =========================================================

def generate_short_description(row):

    product_name = generate_product_name(row)

    part_number = clean_text(
        row.get("Mfg_Part_Num", "")
    )

    brand = clean_text(
        row.get("Resolved_Brand", "")
    )

    if brand and brand != "Unknown":

        return (
            f"{product_name} "
            f"for industrial and commercial applications."
        )

    return (
        f"{product_name} "
        f"for industrial and commercial applications."
    )


# =========================================================
# 6. GENERATE LONG DESCRIPTION
# =========================================================

def generate_long_description(row):

    product_name = generate_product_name(row)

    manufacturer = clean_text(
        row.get("Part_Manuf", "")
    )

    attributes = get_attributes(row)

    text = product_name

    if manufacturer:

        text += (
            f" Manufactured or supplied by "
            f"{manufacturer}."
        )

    if attributes:

        text += (
            " Available product information "
            "includes "
            + ", ".join(attributes[:8])
            + "."
        )

    return text


# =========================================================
# 7. GENERATE MARKETING DESCRIPTION
# =========================================================

def generate_marketing_description(row):

    product_name = generate_product_name(row)

    attributes = get_attributes(row)

    if attributes:

        attribute_text = ", ".join(
            attributes[:5]
        )

        return (
            f"{product_name} designed for "
            f"industrial and commercial use. "
            f"Key identified specifications include "
            f"{attribute_text}."
        )

    return (
        f"{product_name} designed for "
        f"industrial and commercial use."
    )


# =========================================================
# 8. GENERATE FEATURES
# =========================================================

def generate_features(row):

    features = []

    brand = clean_text(
        row.get("Resolved_Brand", "")
    )

    manufacturer = clean_text(
        row.get("Part_Manuf", "")
    )

    part_number = clean_text(
        row.get("Mfg_Part_Num", "")
    )

    attributes = get_attributes(row)

    # -----------------------------------------------------
    # Brand
    # -----------------------------------------------------

    if brand and brand != "Unknown":

        features.append(
            f"Brand: {brand}"
        )

    # -----------------------------------------------------
    # Manufacturer
    # -----------------------------------------------------

    if manufacturer:

        features.append(
            f"Manufacturer: {manufacturer}"
        )

    # -----------------------------------------------------
    # Part number
    # -----------------------------------------------------

    if part_number:

        features.append(
            f"Manufacturer Part Number: {part_number}"
        )

    # -----------------------------------------------------
    # Attributes
    # -----------------------------------------------------

    for attribute in attributes:

        features.append(attribute)

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    unique_features = []

    for feature in features:

        if feature not in unique_features:

            unique_features.append(feature)

    return unique_features[:20]


# =========================================================
# 9. CREATE PRODUCT NAME
# =========================================================

print("Generating product names...")

df["Product Name"] = df.apply(
    generate_product_name,
    axis=1
)


# =========================================================
# 10. CREATE SHORT DESCRIPTION
# =========================================================

print("Generating short descriptions...")

df["SHORT_DESC"] = df.apply(
    generate_short_description,
    axis=1
)


# =========================================================
# 11. CREATE LONG DESCRIPTION
# =========================================================

print("Generating long descriptions...")

df["LONG_DESC1"] = df.apply(
    generate_long_description,
    axis=1
)


# =========================================================
# 12. CREATE MARKETING DESCRIPTION
# =========================================================

print("Generating marketing descriptions...")

df["MARKETING_DESCRIPTION"] = df.apply(
    generate_marketing_description,
    axis=1
)


# =========================================================
# 13. CREATE 20 FEATURE FIELDS
# =========================================================

print("Generating product features...")

for i in range(1, 21):

    df[
        f"ITEM_FEATURES_{i}"
    ] = ""


# =========================================================
# 14. FILL FEATURE FIELDS
# =========================================================

for index, row in df.iterrows():

    features = generate_features(row)

    for position, feature in enumerate(
        features,
        start=1
    ):

        if position <= 20:

            df.loc[
                index,
                f"ITEM_FEATURES_{position}"
            ] = feature


# =========================================================
# 15. BASIC DELIVERY FIELDS
# =========================================================

df["MANUFACTURER_NAME"] = df[
    "Part_Manuf"
]

df["BRAND_NAME"] = df[
    "Resolved_Brand"
]

df["MANUFACTURER_PART_NUMBER"] = df[
    "Mfg_Part_Num"
]


# =========================================================
# 16. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "output",
    exist_ok=True
)


# =========================================================
# 17. SAVE OUTPUT
# =========================================================

df.to_csv(
    output_file,
    index=False
)


# =========================================================
# 18. SUMMARY
# =========================================================

print()
print("=" * 60)
print("PRODUCT CONTENT GENERATOR")
print("=" * 60)

print(
    "Products processed:",
    len(df)
)

print(
    "Product names generated:",
    df["Product Name"].notna().sum()
)

print(
    "Short descriptions generated:",
    df["SHORT_DESC"].notna().sum()
)

print(
    "Long descriptions generated:",
    df["LONG_DESC1"].notna().sum()
)

print(
    "Marketing descriptions generated:",
    df["MARKETING_DESCRIPTION"].notna().sum()
)


# =========================================================
# 19. SHOW EXAMPLE
# =========================================================

print()
print("===== SAMPLE GENERATED CONTENT =====")

for i in range(min(3, len(df))):

    print()
    print(
        "PRODUCT:",
        df.loc[i, "Product Name"]
    )

    print(
        "SHORT:",
        df.loc[i, "SHORT_DESC"]
    )

    print(
        "LONG:",
        df.loc[i, "LONG_DESC1"]
    )

    print(
        "MARKETING:",
        df.loc[
            i,
            "MARKETING_DESCRIPTION"
        ]
    )

    print("FEATURES:")

    for j in range(1, 21):

        feature = clean_text(
            df.loc[
                i,
                f"ITEM_FEATURES_{j}"
            ]
        )

        if feature:

            print(
                f"  {j}. {feature}"
            )


# =========================================================
# 20. FINAL OUTPUT
# =========================================================

print()
print("Output saved to:")
print(output_file)

print()
print(
    "ProductIQ Content Generator completed successfully! 🚀"
)