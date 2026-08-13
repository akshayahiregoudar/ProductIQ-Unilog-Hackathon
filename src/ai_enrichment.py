import pandas as pd
import os
import re


# =========================================================
# PRODUCTIQ - AI-READY ENRICHMENT ENGINE
# =========================================================

INPUT_FILE = "output/productiq_evidence.csv"
OUTPUT_FILE = "output/productiq_ai_enriched.csv"


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("PRODUCTIQ AI ENRICHMENT ENGINE")
print("=" * 60)

print("Products loaded:", len(df))


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def get_attributes(row):

    attributes = []

    for i in range(1, 51):

        label = clean(
            row.get(f"ATTRIBUTE_LABEL {i}", "")
        )

        value = clean(
            row.get(f"ATTRIBUTE_VALUE {i}", "")
        )

        uom = clean(
            row.get(f"ATTRIBUTE_UOM {i}", "")
        )

        if label and value:

            if uom:
                attributes.append(
                    f"{label}: {value} {uom}"
                )
            else:
                attributes.append(
                    f"{label}: {value}"
                )

    return attributes


# =========================================================
# PRODUCT TYPE DETECTION
# =========================================================

def detect_product_type(description):

    text = description.lower()

    product_types = {

        "cut-off disc": [
            "cut-off disc",
            "cut off disc"
        ],

        "abrasive disc": [
            "abrasive disc",
            "film disc",
            "disc/box"
        ],

        "sanding belt": [
            "sanding belt",
            "belt"
        ],

        "abrasive sheet": [
            "abrasive sheet",
            "sandpaper"
        ],

        "drill bit": [
            "drill bit",
            "drill"
        ],

        "saw blade": [
            "saw blade",
            "blade"
        ],

        "grinding wheel": [
            "grinding wheel",
            "grinding"
        ],

        "light fixture": [
            "light",
            "fixture",
            "led"
        ],

        "electrical product": [
            "switch",
            "wire",
            "cable",
            "outlet",
            "receptacle"
        ]
    }

    for product_type, keywords in product_types.items():

        for keyword in keywords:

            if keyword in text:
                return product_type

    return "Industrial product"


# =========================================================
# APPLICATION DETECTION
# =========================================================

def detect_application(product_type, description):

    text = description.lower()

    if "cut-off disc" in text or "cut off disc" in text:

        return "Metal cutting applications"

    if "sanding belt" in text:

        return "Sanding and surface preparation"

    if "abrasive" in text or "disc" in text:

        return "Surface preparation and finishing"

    if "drill" in text:

        return "Drilling applications"

    if "saw blade" in text or "blade" in text:

        return "Cutting applications"

    if "light" in text or "led" in text:

        return "Lighting applications"

    if (
        "wire" in text
        or "cable" in text
        or "switch" in text
    ):

        return "Electrical applications"

    return "Industrial and commercial applications"


# =========================================================
# KEY FEATURES
# =========================================================

def generate_features(row):

    features = []

    brand = clean(
        row.get("Resolved_Brand", "")
    )

    manufacturer = clean(
        row.get("Part_Manuf", "")
    )

    part_number = clean(
        row.get("Mfg_Part_Num", "")
    )

    description = clean(
        row.get("Part_Desc", "")
    )

    attributes = get_attributes(row)

    # Brand
    if brand and brand != "Unknown":

        features.append(
            f"Brand: {brand}"
        )

    # Manufacturer
    if manufacturer:

        features.append(
            f"Manufacturer: {manufacturer}"
        )

    # Part number
    if part_number:

        features.append(
            f"Part Number: {part_number}"
        )

    # Product type
    product_type = detect_product_type(
        description
    )

    features.append(
        f"Product Type: {product_type}"
    )

    # Application
    application = detect_application(
        product_type,
        description
    )

    features.append(
        f"Application: {application}"
    )

    # Technical attributes
    for attribute in attributes:

        if attribute not in features:

            features.append(attribute)

    return features[:20]


# =========================================================
# AI-STYLE PRODUCT NAME
# =========================================================

def generate_ai_product_name(row):

    description = clean(
        row.get("Part_Desc", "")
    )

    brand = clean(
        row.get("Resolved_Brand", "")
    )

    part_number = clean(
        row.get("Mfg_Part_Num", "")
    )

    product_type = detect_product_type(
        description
    )

    # Remove part number from beginning
    cleaned_description = description

    if part_number:

        cleaned_description = re.sub(
            re.escape(part_number),
            "",
            cleaned_description,
            flags=re.IGNORECASE
        ).strip()

    # Use original description if cleaning removed everything
    if not cleaned_description:

        cleaned_description = description

    if brand and brand != "Unknown":

        if brand.lower() not in cleaned_description.lower():

            return (
                f"{brand} {cleaned_description}"
            )

    return cleaned_description


# =========================================================
# AI-STYLE APPLICATION DESCRIPTION
# =========================================================

def generate_ai_description(row):

    product_name = generate_ai_product_name(
        row
    )

    description = clean(
        row.get("Part_Desc", "")
    )

    product_type = detect_product_type(
        description
    )

    application = detect_application(
        product_type,
        description
    )

    attributes = get_attributes(row)

    text = (
        f"{product_name} is an "
        f"{product_type} intended for "
        f"{application.lower()}."
    )

    if attributes:

        text += (
            " Identified product specifications "
            "include "
            + ", ".join(attributes[:5])
            + "."
        )

    return text


# =========================================================
# CONFIDENCE
# =========================================================

def calculate_ai_confidence(row):

    score = 0.0

    brand = clean(
        row.get("Resolved_Brand", "")
    )

    description = clean(
        row.get("Part_Desc", "")
    )

    manufacturer = clean(
        row.get("Part_Manuf", "")
    )

    attribute_count = 0

    for i in range(1, 51):

        label = clean(
            row.get(
                f"ATTRIBUTE_LABEL {i}",
                ""
            )
        )

        value = clean(
            row.get(
                f"ATTRIBUTE_VALUE {i}",
                ""
            )
        )

        if label and value:

            attribute_count += 1

    # Description
    if description:
        score += 0.30

    # Manufacturer
    if manufacturer:
        score += 0.20

    # Brand
    if brand and brand != "Unknown":
        score += 0.25

    # Attributes
    if attribute_count >= 3:
        score += 0.25

    elif attribute_count >= 1:
        score += 0.15

    return round(
        min(score, 1.0),
        2
    )


# =========================================================
# GENERATE AI-STYLE ENRICHMENT
# =========================================================

print("\nGenerating AI-ready product intelligence...")

df["AI_Product_Name"] = df.apply(
    generate_ai_product_name,
    axis=1
)

df["AI_Product_Type"] = df[
    "Part_Desc"
].apply(
    lambda x: detect_product_type(
        clean(x)
    )
)

df["AI_Application"] = df.apply(
    lambda row: detect_application(
        row["AI_Product_Type"],
        clean(row.get("Part_Desc", ""))
    ),
    axis=1
)

df["AI_Description"] = df.apply(
    generate_ai_description,
    axis=1
)

df["AI_Confidence"] = df.apply(
    calculate_ai_confidence,
    axis=1
)


# =========================================================
# AI FEATURES
# =========================================================

for i in range(1, 21):

    df[
        f"AI_FEATURE_{i}"
    ] = ""


for index, row in df.iterrows():

    features = generate_features(row)

    for position, feature in enumerate(
        features,
        start=1
    ):

        if position <= 20:

            df.loc[
                index,
                f"AI_FEATURE_{position}"
            ] = feature


# =========================================================
# AI DECISION
# =========================================================

def ai_decision(confidence):

    if confidence >= 0.80:

        return "AUTO_ACCEPT"

    elif confidence >= 0.50:

        return "REVIEW"

    return "HUMAN_REVIEW"


df["AI_Decision"] = df[
    "AI_Confidence"
].apply(
    ai_decision
)


# =========================================================
# AI EVIDENCE
# =========================================================

df["AI_Evidence"] = df.apply(
    lambda row:
    (
        "Generated from product description, "
        "manufacturer information, brand evidence "
        "and extracted technical attributes."
    ),
    axis=1
)


# =========================================================
# SAVE
# =========================================================

os.makedirs(
    "output",
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# SUMMARY
# =========================================================

print()
print("=" * 60)
print("AI ENRICHMENT SUMMARY")
print("=" * 60)

print(
    "Products processed:",
    len(df)
)

print()
print("===== PRODUCT TYPES =====")

print(
    df["AI_Product_Type"]
    .value_counts()
    .head(10)
)

print()
print("===== AI DECISIONS =====")

print(
    df["AI_Decision"]
    .value_counts()
)

print()
print("===== CONFIDENCE =====")

print(
    df["AI_Confidence"]
    .describe()
)


# =========================================================
# EXAMPLES
# =========================================================

print()
print("===== AI ENRICHMENT EXAMPLES =====")

for i in range(min(5, len(df))):

    print()
    print(
        "Product:",
        df.loc[
            i,
            "AI_Product_Name"
        ]
    )

    print(
        "Product Type:",
        df.loc[
            i,
            "AI_Product_Type"
        ]
    )

    print(
        "Application:",
        df.loc[
            i,
            "AI_Application"
        ]
    )

    print(
        "Description:",
        df.loc[
            i,
            "AI_Description"
        ]
    )

    print(
        "Confidence:",
        df.loc[
            i,
            "AI_Confidence"
        ]
    )

    print(
        "Decision:",
        df.loc[
            i,
            "AI_Decision"
        ]
    )


# =========================================================
# FINAL OUTPUT
# =========================================================

print()
print("Output saved to:")
print(OUTPUT_FILE)

print()
print(
    "ProductIQ AI Enrichment completed successfully! 🚀"
)