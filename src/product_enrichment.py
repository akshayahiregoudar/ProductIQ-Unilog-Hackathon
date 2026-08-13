import pandas as pd
import re
import os


# =========================================================
# 1. FILE PATHS
# =========================================================

input_file = "data/Unihack_ Sample Dataset - Input.csv"
output_file = "output/productiq_enriched_products.csv"


# =========================================================
# 2. LOAD DATA
# =========================================================

df = pd.read_csv(input_file)

print("Dataset loaded successfully!")
print("Rows:", len(df))


# =========================================================
# 3. CLEAN PLACEHOLDER VALUES
# =========================================================

missing_values = [
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --"
]

for value in missing_values:
    df = df.replace(value, pd.NA)


# =========================================================
# 4. KNOWN BRANDS
# =========================================================

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
    "Rheem",
    "Mirka",
    "Hager",
    "Provia",
    "James Hardie",
    "Andersen",
    "AJM",
    "Westbury",
    "Century Components",
    "Nicholson",
    "Hunter",
    "First Alert",
    "BRK",
    "Square D",
    "Feit Electric",
    "Wiz",
    "Prime",
    "StealthMounts",
    "Police Security"
]


# =========================================================
# 5. FIND BRAND IN DESCRIPTION
# =========================================================

def find_brand_in_description(description):

    text = str(description).lower()

    for brand in known_brands:

        if brand.lower() in text:
            return brand

    return None


# =========================================================
# 6. RESOLVE BRAND
# =========================================================

def resolve_brand(row):

    candidates = []

    # Structured brand sources
    for column in [
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand"
    ]:

        value = row[column]

        if pd.notna(value):

            candidates.append(
                str(value).strip()
            )

    # Description evidence
    description_brand = find_brand_in_description(
        row["Part_Desc"]
    )

    if description_brand:

        candidates.append(
            description_brand
        )

    # No evidence
    if not candidates:

        return (
            "Unknown",
            0.0,
            "No evidence"
        )

    # Count evidence
    counts = {}

    for brand in candidates:

        counts[brand] = (
            counts.get(brand, 0) + 1
        )

    best_brand = max(
        counts,
        key=counts.get
    )

    evidence_count = counts[best_brand]

    # Count structured evidence
    structured_count = 0

    for column in [
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand"
    ]:

        if pd.notna(row[column]):

            structured_count += 1

    # Confidence
    if structured_count >= 2 and evidence_count >= 2:

        confidence = 0.95
        source = "Multiple structured sources"

    elif structured_count >= 1 and description_brand:

        confidence = 0.90
        source = "Structured source + description"

    elif structured_count >= 1:

        confidence = 0.70
        source = "Structured source"

    elif description_brand:

        confidence = 0.60
        source = "Product description"

    else:

        confidence = 0.0
        source = "No evidence"

    return (
        best_brand,
        confidence,
        source
    )


# =========================================================
# 7. EXTRACT PRODUCT ATTRIBUTES
# =========================================================

def extract_attributes(text):

    text = str(text)

    attributes = []

    # =====================================================
    # VOLTAGE
    # =====================================================

    voltage_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[Vv]\b',
        text
    )

    if voltage_match:

        attributes.append(
            (
                "Voltage",
                voltage_match.group(1),
                "V"
            )
        )


    # =====================================================
    # AMPERAGE
    # =====================================================

    amperage_patterns = [

        r'amperage(?:\s+rating)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*[Aa]\b',

        r'(\d+(?:\.\d+)?)\s*amps?\b',

        r'(\d+(?:\.\d+)?)\s*amperes?\b',

        r'current\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*[Aa]\b'
    ]

    for pattern in amperage_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            attributes.append(
                (
                    "Amperage",
                    match.group(1),
                    "A"
                )
            )

            break


    # =====================================================
    # SOUND LEVEL
    # =====================================================

    sound_match = re.search(
        r'(\d+(?:\.\d+)?)\s*dBA\b',
        text,
        re.IGNORECASE
    )

    if sound_match:

        attributes.append(
            (
                "Sound Level",
                sound_match.group(1),
                "dBA"
            )
        )


    # =====================================================
    # FRACTIONAL SIZE
    # =====================================================

    # Example:
    # 6-1/2"
    # 1-1/4"
    # 3-1/2"

    mixed_fraction = re.search(
        r'(\d+)\s*-\s*(\d+/\d+)\s*(?:["”]|inch|in\b)',
        text,
        re.IGNORECASE
    )

    if mixed_fraction:

        value = (
            mixed_fraction.group(1)
            + "-"
            + mixed_fraction.group(2)
        )

        attributes.append(
            (
                "Size",
                value,
                "in"
            )
        )

    else:

        # Example:
        # 1/2"
        # 3/4"
        # 7/8"

        fraction = re.search(
            r'\b(\d+/\d+)\s*(?:["”]|inch|in\b)',
            text,
            re.IGNORECASE
        )

        if fraction:

            attributes.append(
                (
                    "Size",
                    fraction.group(1),
                    "in"
                )
            )


    # =====================================================
    # DIMENSION PATTERN
    # =====================================================

    # Example:
    # 2.75x30
    # 5x10
    # 2.75 x 30

    dimension_match = re.search(
        r'\b(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\b',
        text
    )

    if dimension_match:

        attributes.append(
            (
                "Dimension",
                dimension_match.group(1)
                + " x "
                + dimension_match.group(2),
                ""
            )
        )


    # =====================================================
    # SIMPLE INCH SIZE
    # =====================================================

    # Only detect a simple inch value when it is NOT
    # already part of a fraction or dimension.

    simple_inch = re.search(
        r'(?<![/\d-])(\d+(?:\.\d+)?)\s*(?:["”]|inch|in\b)',
        text,
        re.IGNORECASE
    )

    if simple_inch:

        value = simple_inch.group(1)

        already_exists = any(
            item[0] == "Size"
            and item[1] == value
            for item in attributes
        )

        if not already_exists:

            attributes.append(
                (
                    "Size",
                    value,
                    "in"
                )
            )


    # =====================================================
    # MILLIMETER
    # =====================================================

    mm_match = re.search(
        r'\b(\d+(?:\.\d+)?)\s*mm\b',
        text,
        re.IGNORECASE
    )

    if mm_match:

        attributes.append(
            (
                "Measurement",
                mm_match.group(1),
                "mm"
            )
        )


    # =====================================================
    # GRIT
    # =====================================================

    grit_match = re.search(
        r'\bP(\d{2,4})\b',
        text,
        re.IGNORECASE
    )

    if grit_match:

        attributes.append(
            (
                "Grit",
                "P" + grit_match.group(1),
                ""
            )
        )


    # =====================================================
    # QUANTITY
    # =====================================================

    quantity_match = re.search(
        r'\b(\d+)\s*(?:pc|pcs|piece|pieces|pack|packs)\b',
        text,
        re.IGNORECASE
    )

    if quantity_match:

        attributes.append(
            (
                "Quantity",
                quantity_match.group(1),
                "pcs"
            )
        )


    # =====================================================
    # WEIGHT
    # =====================================================

    weight_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(lb|lbs|pound|pounds)\b',
        text,
        re.IGNORECASE
    )

    if weight_match:

        attributes.append(
            (
                "Weight",
                weight_match.group(1),
                "lb"
            )
        )


    return attributes


# =========================================================
# 8. RESOLVE BRANDS
# =========================================================

print("\nResolving brands...")

brand_results = df.apply(
    resolve_brand,
    axis=1
)

df["Resolved_Brand"] = brand_results.apply(
    lambda x: x[0]
)

df["Brand_Confidence"] = brand_results.apply(
    lambda x: x[1]
)

df["Brand_Source"] = brand_results.apply(
    lambda x: x[2]
)


# =========================================================
# 9. EXTRACT ATTRIBUTES
# =========================================================

print("Extracting attributes...")

df["Extracted_Attributes"] = df[
    "Part_Desc"
].apply(
    extract_attributes
)


# =========================================================
# 10. CREATE 50 ATTRIBUTE SLOTS
# =========================================================

print("Creating attribute slots...")

for i in range(1, 51):

    df[
        f"ATTRIBUTE_LABEL {i}"
    ] = ""

    df[
        f"ATTRIBUTE_VALUE {i}"
    ] = ""

    df[
        f"ATTRIBUTE_UOM {i}"
    ] = ""


# =========================================================
# 11. FILL ATTRIBUTE SLOTS
# =========================================================

for index, attributes in enumerate(
    df["Extracted_Attributes"]
):

    for slot, attribute in enumerate(
        attributes[:50],
        start=1
    ):

        label, value, uom = attribute

        df.loc[
            index,
            f"ATTRIBUTE_LABEL {slot}"
        ] = label

        df.loc[
            index,
            f"ATTRIBUTE_VALUE {slot}"
        ] = value

        df.loc[
            index,
            f"ATTRIBUTE_UOM {slot}"
        ] = uom


# =========================================================
# 12. BASIC DELIVERY FIELDS
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

df["Product Name"] = df[
    "Part_Desc"
]


# =========================================================
# 13. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "output",
    exist_ok=True
)


# =========================================================
# 14. SAVE OUTPUT
# =========================================================

df.to_csv(
    output_file,
    index=False
)


# =========================================================
# 15. SUMMARY
# =========================================================

print("\n")
print("=" * 60)
print("PRODUCTIQ ATTRIBUTE ENGINE")
print("=" * 60)

print(
    "\nProducts processed:",
    len(df)
)

print(
    "Brands identified:",
    (
        df["Resolved_Brand"] != "Unknown"
    ).sum()
)

print(
    "Products with extracted attributes:",
    (
        df["Extracted_Attributes"]
        .apply(len)
        .gt(0)
        .sum()
    )
)

print(
    "Voltage found:",
    sum(
        any(
            attribute[0] == "Voltage"
            for attribute in attributes
        )
        for attributes in df["Extracted_Attributes"]
    )
)

print(
    "Amperage found:",
    sum(
        any(
            attribute[0] == "Amperage"
            for attribute in attributes
        )
        for attributes in df["Extracted_Attributes"]
    )
)

print(
    "Sound level found:",
    sum(
        any(
            attribute[0] == "Sound Level"
            for attribute in attributes
        )
        for attributes in df["Extracted_Attributes"]
    )
)


# =========================================================
# 16. SAVE ATTRIBUTE-ONLY VIEW
# =========================================================

attribute_file = (
    "output/productiq_attributes.csv"
)

attribute_columns = [
    "Mfg_Part_Num",
    "Part_Desc",
    "Resolved_Brand",
    "Brand_Confidence",
    "Brand_Source"
]

for i in range(1, 51):

    attribute_columns.extend([
        f"ATTRIBUTE_LABEL {i}",
        f"ATTRIBUTE_VALUE {i}",
        f"ATTRIBUTE_UOM {i}"
    ])

df[
    attribute_columns
].to_csv(
    attribute_file,
    index=False
)


# =========================================================
# 17. SHOW EXAMPLES
# =========================================================

print("\n===== ATTRIBUTE EXAMPLES =====")

for i in range(
    min(10, len(df))
):

    print(
        "\nProduct:",
        df.loc[i, "Part_Desc"]
    )

    attributes = df.loc[
        i,
        "Extracted_Attributes"
    ]

    if attributes:

        for attribute in attributes:

            print(
                "  ",
                attribute
            )

    else:

        print(
            "   No attributes detected"
        )


# =========================================================
# 18. OUTPUT LOCATIONS
# =========================================================

print("\n===== OUTPUT FILES =====")

print(
    "Main output:",
    output_file
)

print(
    "Attribute output:",
    attribute_file
)

print(
    "\nProductIQ Attribute Engine completed successfully! 🚀"
)