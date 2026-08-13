import pandas as pd
import os


# =========================================================
# 1. FILE PATHS
# =========================================================

input_file = "output/productiq_validated.csv"
output_file = "output/productiq_evidence.csv"


# =========================================================
# 2. LOAD DATA
# =========================================================

df = pd.read_csv(input_file)

print("Validated dataset loaded!")
print("Products:", len(df))


# =========================================================
# 3. HELPER FUNCTION
# =========================================================

def clean(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# =========================================================
# 4. CREATE EVIDENCE FOR ONE PRODUCT
# =========================================================

def create_evidence(row):

    evidence_items = []

    # -----------------------------------------------------
    # Product description evidence
    # -----------------------------------------------------

    description = clean(
        row.get("Part_Desc", "")
    )

    if description:

        evidence_items.append(
            "Product description"
        )


    # -----------------------------------------------------
    # Manufacturer evidence
    # -----------------------------------------------------

    manufacturer = clean(
        row.get("Part_Manuf", "")
    )

    if manufacturer:

        evidence_items.append(
            "Manufacturer field"
        )


    # -----------------------------------------------------
    # Brand evidence
    # -----------------------------------------------------

    brand = clean(
        row.get("Resolved_Brand", "")
    )

    brand_source = clean(
        row.get("Brand_Source", "")
    )

    brand_confidence = clean(
        row.get("Brand_Confidence", "")
    )

    if brand and brand != "Unknown":

        evidence_items.append(
            f"Brand: {brand} "
            f"(source: {brand_source}, "
            f"confidence: {brand_confidence})"
        )


    # -----------------------------------------------------
    # Attribute evidence
    # -----------------------------------------------------

    attribute_evidence = []

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

        uom = clean(
            row.get(
                f"ATTRIBUTE_UOM {i}",
                ""
            )
        )

        if label and value:

            if uom:

                attribute_evidence.append(
                    f"{label}={value} {uom}"
                )

            else:

                attribute_evidence.append(
                    f"{label}={value}"
                )


    # -----------------------------------------------------
    # Combine evidence
    # -----------------------------------------------------

    if attribute_evidence:

        evidence_items.append(
            "Extracted attributes: "
            + ", ".join(attribute_evidence)
        )


    # -----------------------------------------------------
    # Validation evidence
    # -----------------------------------------------------

    validation_status = clean(
        row.get(
            "Validation_Status",
            ""
        )
    )

    validation_score = clean(
        row.get(
            "Validation_Score",
            ""
        )
    )

    validation_evidence = clean(
        row.get(
            "Validation_Evidence",
            ""
        )
    )

    if validation_status:

        evidence_items.append(
            f"Validation: {validation_status} "
            f"(score: {validation_score})"
        )

    if validation_evidence:

        evidence_items.append(
            f"Validation evidence: "
            f"{validation_evidence}"
        )


    # -----------------------------------------------------
    # Final evidence text
    # -----------------------------------------------------

    if evidence_items:

        return " | ".join(
            evidence_items
        )

    return "No evidence available"


# =========================================================
# 5. CREATE EVIDENCE
# =========================================================

print("\nGenerating evidence records...")

df["Evidence_Summary"] = df.apply(
    create_evidence,
    axis=1
)


# =========================================================
# 6. EVIDENCE SOURCE TYPE
# =========================================================

def determine_source_type(row):

    sources = []

    description = clean(
        row.get("Part_Desc", "")
    )

    manufacturer = clean(
        row.get("Part_Manuf", "")
    )

    brand_source = clean(
        row.get("Brand_Source", "")
    )

    if description:

        sources.append(
            "Product Description"
        )

    if manufacturer:

        sources.append(
            "Manufacturer Field"
        )

    if brand_source:

        sources.append(
            brand_source
        )

    if sources:

        return " + ".join(
            dict.fromkeys(sources)
        )

    return "No Source"


df["Evidence_Source_Type"] = df.apply(
    determine_source_type,
    axis=1
)


# =========================================================
# 7. EVIDENCE COUNT
# =========================================================

def count_evidence(row):

    count = 0

    if clean(row.get("Part_Desc", "")):
        count += 1

    if clean(row.get("Part_Manuf", "")):
        count += 1

    if (
        clean(row.get("Resolved_Brand", ""))
        and
        clean(row.get("Resolved_Brand", "")) != "Unknown"
    ):
        count += 1

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

            count += 1

    return count


df["Evidence_Count"] = df.apply(
    count_evidence,
    axis=1
)


# =========================================================
# 8. EVIDENCE QUALITY
# =========================================================

def evidence_quality(row):

    count = row["Evidence_Count"]

    try:
        count = int(count)
    except:
        count = 0

    validation_status = clean(
        row.get(
            "Validation_Status",
            ""
        )
    )

    if count >= 6 and validation_status == "PASS":

        return "HIGH"

    elif count >= 3:

        return "MEDIUM"

    elif count >= 1:

        return "LOW"

    return "NONE"


df["Evidence_Quality"] = df.apply(
    evidence_quality,
    axis=1
)


# =========================================================
# 9. HUMAN REVIEW FLAG
# =========================================================

def review_required(row):

    validation_status = clean(
        row.get(
            "Validation_Status",
            ""
        )
    )

    evidence_quality = clean(
        row.get(
            "Evidence_Quality",
            ""
        )
    )

    if validation_status == "LOW_CONFIDENCE":

        return "YES"

    if evidence_quality in [
        "LOW",
        "NONE"
    ]:

        return "YES"

    return "NO"


df["Human_Review_Required"] = df.apply(
    review_required,
    axis=1
)


# =========================================================
# 10. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "output",
    exist_ok=True
)


# =========================================================
# 11. SAVE OUTPUT
# =========================================================

df.to_csv(
    output_file,
    index=False
)


# =========================================================
# 12. SUMMARY
# =========================================================

print()
print("=" * 60)
print("PRODUCTIQ EVIDENCE ENGINE")
print("=" * 60)

print(
    "\nProducts processed:",
    len(df)
)

print(
    "\n===== EVIDENCE QUALITY ====="
)

print(
    df["Evidence_Quality"]
    .value_counts()
)

print(
    "\n===== HUMAN REVIEW ====="
)

print(
    df["Human_Review_Required"]
    .value_counts()
)

print(
    "\n===== AVERAGE EVIDENCE COUNT ====="
)

print(
    round(
        df["Evidence_Count"].mean(),
        2
    )
)


# =========================================================
# 13. SHOW EXAMPLES
# =========================================================

print()
print(
    "===== EVIDENCE EXAMPLES ====="
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
        "Evidence:",
        df.loc[
            i,
            "Evidence_Summary"
        ]
    )

    print(
        "Source Type:",
        df.loc[
            i,
            "Evidence_Source_Type"
        ]
    )

    print(
        "Evidence Count:",
        df.loc[
            i,
            "Evidence_Count"
        ]
    )

    print(
        "Evidence Quality:",
        df.loc[
            i,
            "Evidence_Quality"
        ]
    )

    print(
        "Human Review:",
        df.loc[
            i,
            "Human_Review_Required"
        ]
    )


# =========================================================
# 14. OUTPUT
# =========================================================

print()
print(
    "Output saved to:"
)

print(output_file)

print()
print(
    "ProductIQ Evidence Engine completed successfully! 🚀"
)