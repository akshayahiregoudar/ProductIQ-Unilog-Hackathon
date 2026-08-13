import pandas as pd
import os


# =========================================================
# 1. FILE PATHS
# =========================================================

input_file = "output/productiq_content_enriched.csv"
output_file = "output/productiq_validated.csv"


# =========================================================
# 2. LOAD DATA
# =========================================================

df = pd.read_csv(input_file)

print("Content-enriched dataset loaded!")
print("Products:", len(df))


# =========================================================
# 3. HELPER
# =========================================================

def clean(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# =========================================================
# 4. VALIDATE ONE PRODUCT
# =========================================================

def validate_product(row):

    score = 0
    issues = []
    evidence = []

    # -----------------------------------------------------
    # Part number
    # -----------------------------------------------------

    part_number = clean(
        row.get("Mfg_Part_Num", "")
    )

    if part_number:

        score += 20
        evidence.append(
            "Manufacturer part number available"
        )

    else:

        issues.append(
            "Missing manufacturer part number"
        )


    # -----------------------------------------------------
    # Product description
    # -----------------------------------------------------

    description = clean(
        row.get("Part_Desc", "")
    )

    if description:

        score += 20
        evidence.append(
            "Product description available"
        )

    else:

        issues.append(
            "Missing product description"
        )


    # -----------------------------------------------------
    # Manufacturer
    # -----------------------------------------------------

    manufacturer = clean(
        row.get("Part_Manuf", "")
    )

    if manufacturer:

        score += 15
        evidence.append(
            "Manufacturer available"
        )

    else:

        issues.append(
            "Missing manufacturer"
        )


    # -----------------------------------------------------
    # Brand
    # -----------------------------------------------------

    brand = clean(
        row.get("Resolved_Brand", "")
    )

    confidence = row.get(
        "Brand_Confidence",
        0
    )

    try:

        confidence = float(confidence)

    except:

        confidence = 0


    if brand and brand != "Unknown":

        if confidence >= 0.9:

            score += 20
            evidence.append(
                "High-confidence brand"
            )

        elif confidence >= 0.6:

            score += 15
            evidence.append(
                "Medium-confidence brand"
            )

        else:

            score += 5
            issues.append(
                "Low-confidence brand"
            )

    else:

        issues.append(
            "Brand could not be resolved"
        )


    # -----------------------------------------------------
    # Attributes
    # -----------------------------------------------------

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


    if attribute_count >= 3:

        score += 15
        evidence.append(
            f"{attribute_count} technical attributes detected"
        )

    elif attribute_count >= 1:

        score += 8
        evidence.append(
            f"{attribute_count} technical attribute detected"
        )

    else:

        issues.append(
            "No technical attributes detected"
        )


    # =====================================================
    # VALIDATION STATUS
    # =====================================================

    if score >= 85:

        status = "PASS"

    elif score >= 65:

        status = "REVIEW"

    else:

        status = "LOW_CONFIDENCE"


    # =====================================================
    # ISSUE TEXT
    # =====================================================

    if issues:

        issue_text = "; ".join(
            issues
        )

    else:

        issue_text = "No major issues detected"


    # =====================================================
    # EVIDENCE TEXT
    # =====================================================

    if evidence:

        evidence_text = "; ".join(
            evidence
        )

    else:

        evidence_text = "No evidence"


    return (
        score,
        status,
        issue_text,
        evidence_text,
        attribute_count
    )


# =========================================================
# 5. RUN VALIDATION
# =========================================================

print("\nValidating products...")

results = df.apply(
    validate_product,
    axis=1
)


# =========================================================
# 6. ADD VALIDATION COLUMNS
# =========================================================

df["Validation_Score"] = results.apply(
    lambda x: x[0]
)

df["Validation_Status"] = results.apply(
    lambda x: x[1]
)

df["Validation_Issues"] = results.apply(
    lambda x: x[2]
)

df["Validation_Evidence"] = results.apply(
    lambda x: x[3]
)

df["Detected_Attribute_Count"] = results.apply(
    lambda x: x[4]
)


# =========================================================
# 7. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "output",
    exist_ok=True
)


# =========================================================
# 8. SAVE
# =========================================================

df.to_csv(
    output_file,
    index=False
)


# =========================================================
# 9. SUMMARY
# =========================================================

print()
print("=" * 60)
print("PRODUCTIQ VALIDATION ENGINE")
print("=" * 60)

print(
    "\nTotal products:",
    len(df)
)

print(
    "\n===== VALIDATION STATUS ====="
)

print(
    df["Validation_Status"]
    .value_counts()
)


print(
    "\n===== SCORE SUMMARY ====="
)

print(
    df["Validation_Score"]
    .describe()
)


# =========================================================
# 10. SHOW EXAMPLES
# =========================================================

print()
print(
    "===== VALIDATION EXAMPLES ====="
)

for i in range(min(5, len(df))):

    print()

    print(
        "Product:",
        df.loc[
            i,
            "Part_Desc"
        ]
    )

    print(
        "Brand:",
        df.loc[
            i,
            "Resolved_Brand"
        ]
    )

    print(
        "Score:",
        df.loc[
            i,
            "Validation_Score"
        ]
    )

    print(
        "Status:",
        df.loc[
            i,
            "Validation_Status"
        ]
    )

    print(
        "Issues:",
        df.loc[
            i,
            "Validation_Issues"
        ]
    )

    print(
        "Evidence:",
        df.loc[
            i,
            "Validation_Evidence"
        ]
    )


# =========================================================
# 11. OUTPUT
# =========================================================

print()
print(
    "Output saved to:"
)

print(output_file)

print()
print(
    "ProductIQ Validation Engine completed successfully! 🚀"
)