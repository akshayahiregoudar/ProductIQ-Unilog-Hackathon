import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="ProductIQ",
    page_icon="🤖",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

FINAL_FILE = OUTPUT_DIR / "ProductIQ_Final_Delivery.csv"
ENRICHED_FILE = OUTPUT_DIR / "productiq_enriched_products.csv"
ATTRIBUTE_FILE = OUTPUT_DIR / "productiq_attributes.csv"
EVIDENCE_FILE = OUTPUT_DIR / "productiq_evidence.csv"


@st.cache_data
def load_csv(file_path):
    if not file_path.exists():
        return None

    try:
        return pd.read_csv(
            file_path,
            low_memory=False,
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            file_path,
            low_memory=False,
            encoding="latin1"
        )


df = load_csv(FINAL_FILE)

if df is None:
    df = load_csv(ENRICHED_FILE)

if df is None:
    st.error("ProductIQ output file was not found.")
    st.stop()

enriched_df = load_csv(ENRICHED_FILE)

total_products = len(df)
total_columns = len(df.columns)

filled_cells = int(df.notna().sum().sum())

total_cells = df.shape[0] * df.shape[1]

completion = (
    filled_cells / total_cells * 100
    if total_cells > 0
    else 0
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 ProductIQ")

st.subheader("AI-Powered Product Intelligence Platform")

st.write(
    "Transforming incomplete product information into "
    "**structured, enriched, validated and traceable "
    "product intelligence.**"
)

st.success("✅ ProductIQ data loaded successfully!")

st.divider()


# ============================================================
# METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Products", f"{total_products:,}")

with col2:
    st.metric("📋 Output Columns", f"{total_columns:,}")

with col3:
    st.metric("🧩 Filled Cells", f"{filled_cells:,}")

with col4:
    st.metric("📊 Completion", f"{completion:.2f}%")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤖 ProductIQ")
st.sidebar.caption("AI Product Enrichment Platform")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔎 Product Search",
        "📊 Data Explorer",
        "🏷️ Brand Analysis",
        "⚙️ Attributes",
        "🔍 Evidence",
        "📋 Delivery Output"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.header("🏠 ProductIQ Dashboard")

    st.write(
        "ProductIQ automates product data enrichment through "
        "cleaning, brand resolution, attribute extraction, "
        "content generation, validation and evidence tracking."
    )

    st.divider()

    st.subheader("🔄 Product Enrichment Pipeline")

    pipeline = [
        "Raw Product Data",
        "Data Cleaning",
        "Brand Detection",
        "Brand Resolution",
        "Attribute Extraction",
        "Content Generation",
        "Validation",
        "Evidence Tracking",
        "Final Delivery"
    ]

    cols = st.columns(3)

    for i, step in enumerate(pipeline):
        with cols[i % 3]:
            st.success(f"**{i + 1}. {step}** ✅")

    st.divider()

    st.subheader("📊 Dataset Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.write(f"**Products:** {total_products:,}")
        st.write(f"**Columns:** {total_columns:,}")
        st.write(f"**Filled cells:** {filled_cells:,}")

    with c2:
        st.write(f"**Data completion:** {completion:.2f}%")

        if total_columns == 252:
            st.success("✅ Expected 252-column delivery format")
        else:
            st.warning(
                f"⚠️ Current output has {total_columns} columns"
            )

    st.divider()

    st.subheader("🚀 ProductIQ Capabilities")

    a, b, c = st.columns(3)

    with a:
        st.info(
            """
            **🏷️ Brand Intelligence**

            Detect and resolve product brands
            using available product evidence.
            """
        )

    with b:
        st.info(
            """
            **⚙️ Attribute Extraction**

            Extract technical attributes such as
            grit, diameter, voltage and dimensions.
            """
        )

    with c:
        st.info(
            """
            **🔍 Evidence Tracking**

            Track the source and confidence behind
            enriched product information.
            """
        )


# ============================================================
# PRODUCT SEARCH
# ============================================================

elif page == "🔎 Product Search":

    st.header("🔎 Product Intelligence Search")

    st.write(
        "Search by manufacturer part number, product "
        "description, brand or manufacturer."
    )

    search_text = st.text_input(
        "Enter Product Information",
        placeholder="Example: 3MABR-7100075692"
    )

    if not search_text:
        st.info(
            "👆 Enter a product part number or description above."
        )
        st.stop()

    search_text = search_text.lower().strip()

    search_columns = [
        "Mfg_Part_Num",
        "Part_Desc",
        "MANUFACTURER_PART_NUMBER",
        "BRAND_NAME",
        "MANUFACTURER_NAME",
        "E1_Brand",
        "DIB_Brand",
        "Resolved_Brand"
    ]

    search_columns = [
        c for c in search_columns if c in df.columns
    ]

    mask = pd.Series(False, index=df.index)

    for column in search_columns:
        mask = mask | (
            df[column]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                search_text,
                regex=False,
                na=False
            )
        )

    results = df[mask]

    if len(results) == 0:
        st.warning("❌ No matching product found.")
        st.stop()

    st.success(
        f"✅ {len(results)} matching product(s) found"
    )

    product = results.iloc[0]

    def get_value(row, columns, default="Not available"):

        for column in columns:

            if column in row.index:

                value = row[column]

                if pd.notna(value):

                    text = str(value).strip()

                    if text not in ["", "nan", "None"]:
                        return text

        return default


    part_number = get_value(
        product,
        [
            "Mfg_Part_Num",
            "MANUFACTURER_PART_NUMBER"
        ]
    )

    description = get_value(
        product,
        [
            "Part_Desc",
            "LONG_DESC1",
            "SHORT_DESC"
        ]
    )

    brand = get_value(
        product,
        [
            "BRAND_NAME",
            "Resolved_Brand",
            "E1_Brand",
            "DIB_Brand"
        ],
        "Unknown"
    )

    manufacturer = get_value(
        product,
        [
            "MANUFACTURER_NAME",
            "Part_Manuf"
        ],
        "Unknown"
    )


    # ========================================================
    # BRAND CONFIDENCE FROM ENRICHED FILE
    # ========================================================

    confidence = "Not available"
    source = "Not available"

    if enriched_df is not None:

        if "Mfg_Part_Num" in enriched_df.columns:

            matches = enriched_df[
                enriched_df["Mfg_Part_Num"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                part_number.strip().lower()
            ]

            if len(matches) > 0:

                enriched_product = matches.iloc[0]

                if "Brand_Confidence" in enriched_df.columns:

                    value = enriched_product["Brand_Confidence"]

                    if pd.notna(value):
                        confidence = str(value).strip()

                if "Brand_Source" in enriched_df.columns:

                    value = enriched_product["Brand_Source"]

                    if pd.notna(value):
                        source = str(value).strip()


    # ========================================================
    # PRODUCT
    # ========================================================

    st.divider()

    st.subheader("📦 Product")

    st.title(description)

    st.divider()


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    info1, info2, info3 = st.columns(3)

    with info1:
        st.markdown("### 🔢 Part Number")
        st.info(part_number)

    with info2:
        st.markdown("### 🏷️ Brand")
        st.success(brand)

    with info3:
        st.markdown("### 🏭 Manufacturer")
        st.write(manufacturer)

    st.divider()


    # ========================================================
    # BRAND INTELLIGENCE
    # ========================================================

    st.subheader("🎯 Brand Intelligence")

    brand1, brand2 = st.columns(2)

    with brand1:

        try:

            confidence_number = float(confidence)

            if confidence_number <= 1:
                confidence_number *= 100

            st.metric(
                "Brand Confidence",
                f"{confidence_number:.0f}%"
            )

        except:
            st.metric(
                "Brand Confidence",
                confidence
            )

    with brand2:

        st.metric(
            "Evidence Source",
            source
        )

    st.divider()


    # ========================================================
    # ENRICHED INFORMATION
    # ========================================================

    st.subheader("📝 Enriched Product Information")

    important_fields = [
        "Mfg_Part_Num",
        "Part_Desc",
        "E1_Brand",
        "Unilog_Brand",
        "DIB_Brand",
        "Part_Manuf",
        "MANUFACTURER_NAME",
        "BRAND_NAME",
        "TRADE_NAME",
        "MANUFACTURER_PART_NUMBER",
        "ALTERNATE_PART_NUMBER",
        "MOBILE_DESC",
        "INVOICE_DESC",
        "SHORT_DESC",
        "LONG_DESC1",
        "RETAIL_DESC",
        "MARKETING_DESCRIPTION",
        "APPLICATION",
        "INCLUDES",
        "ITEM_FEATURES_1",
        "ITEM_FEATURES_2",
        "ITEM_FEATURES_3",
        "ITEM_FEATURES_4",
        "Product Name",
        "ATTRIBUTE_LABEL 1"
    ]

    available_fields = [
        field
        for field in important_fields
        if field in df.columns
    ]

    information = []

    for field in available_fields:

        value = product[field]

        if pd.notna(value):

            text = str(value).strip()

            if text not in ["", "nan", "None"]:

                information.append(
                    {
                        "Field": field,
                        "Value": text
                    }
                )

    if information:

        information_df = pd.DataFrame(information)

        st.dataframe(
            information_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No additional enriched information available."
        )

    st.divider()


    # ========================================================
    # ATTRIBUTES
    # ========================================================

    st.subheader("⚙️ Extracted Attributes")

    attribute_df = load_csv(ATTRIBUTE_FILE)

    if attribute_df is not None:

        attribute_mask = pd.Series(
            False,
            index=attribute_df.index
        )

        for column in attribute_df.columns:

            attribute_mask = (
                attribute_mask
                |
                attribute_df[column]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    part_number.lower(),
                    regex=False,
                    na=False
                )
            )

        attribute_results = attribute_df[attribute_mask]

        if len(attribute_results) > 0:

            st.success(
                f"✅ {len(attribute_results)} "
                "attribute record(s) found"
            )

            st.dataframe(
                attribute_results,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No separate attribute record found."
            )

    else:

        st.info(
            "Attribute output file not found."
        )

    st.divider()


    # ========================================================
    # EVIDENCE
    # ========================================================

    st.subheader("🔍 Evidence & Traceability")

    evidence_df = load_csv(EVIDENCE_FILE)

    if evidence_df is not None:

        evidence_mask = pd.Series(
            False,
            index=evidence_df.index
        )

        for column in evidence_df.columns:

            evidence_mask = (
                evidence_mask
                |
                evidence_df[column]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    part_number.lower(),
                    regex=False,
                    na=False
                )
            )

        evidence_results = evidence_df[evidence_mask]

        if len(evidence_results) > 0:

            st.success(
                "✅ Evidence found for this product."
            )

            st.dataframe(
                evidence_results,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No separate evidence record found."
            )

    else:

        st.info(
            "Evidence file not found."
        )

    st.divider()


    # ========================================================
    # COMPLETE RECORD
    # ========================================================

    with st.expander(
        "📋 View Complete 252-Column Record"
    ):

        record_data = []

        for field in df.columns:

            value = product[field]

            if pd.notna(value):

                text = str(value).strip()

                if text not in ["", "nan", "None"]:

                    record_data.append(
                        {
                            "Field": field,
                            "Value": text
                        }
                    )

        complete_df = pd.DataFrame(record_data)

        st.success(
            f"✅ {len(complete_df)} populated fields "
            f"out of {total_columns} total columns"
        )

        st.dataframe(
            complete_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    product_csv = (
        results.head(1)
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "⬇️ Download Product Record",
        data=product_csv,
        file_name="ProductIQ_Product_Record.csv",
        mime="text/csv"
    )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "📊 Data Explorer":

    st.header("📊 Product Data Explorer")

    rows = st.slider(
        "Rows to display",
        5,
        min(100, total_products),
        10
    )

    st.dataframe(
        df.head(rows),
        use_container_width=True,
        height=500
    )

    st.divider()

    st.subheader("📋 Column Information")

    column_info = pd.DataFrame(
        {
            "Column": df.columns,
            "Filled Values": [
                df[c].notna().sum()
                for c in df.columns
            ],
            "Missing Values": [
                df[c].isna().sum()
                for c in df.columns
            ]
        }
    )

    st.dataframe(
        column_info,
        use_container_width=True,
        height=500
    )


# ============================================================
# BRAND ANALYSIS
# ============================================================

elif page == "🏷️ Brand Analysis":

    st.header("🏷️ Brand Intelligence")

    brand_columns = [
        c
        for c in df.columns
        if "brand" in c.lower()
    ]

    if brand_columns:

        selected_brand = st.selectbox(
            "Select Brand Field",
            brand_columns
        )

        brand_counts = (
            df[selected_brand]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(20)
        )

        st.subheader("Top Brands")

        st.bar_chart(brand_counts)

        st.dataframe(
            brand_counts.rename("Products"),
            use_container_width=True
        )

    else:

        st.warning("No brand columns detected.")


# ============================================================
# ATTRIBUTES
# ============================================================

elif page == "⚙️ Attributes":

    st.header("⚙️ Product Attributes")

    attribute_df = load_csv(ATTRIBUTE_FILE)

    if attribute_df is not None:

        st.success(
            f"✅ {len(attribute_df):,} "
            "attribute records loaded."
        )

        st.dataframe(
            attribute_df.head(100),
            use_container_width=True,
            height=500
        )

        csv = (
            attribute_df
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "⬇️ Download Attributes",
            csv,
            "productiq_attributes.csv",
            "text/csv"
        )

    else:

        st.warning(
            "Attribute file not found."
        )


# ============================================================
# EVIDENCE
# ============================================================

elif page == "🔍 Evidence":

    st.header("🔍 Evidence & Traceability")

    evidence_df = load_csv(EVIDENCE_FILE)

    if evidence_df is not None:

        st.success(
            f"✅ {len(evidence_df):,} "
            "evidence records loaded."
        )

        st.dataframe(
            evidence_df.head(100),
            use_container_width=True,
            height=500
        )

        review_columns = [
            c
            for c in evidence_df.columns
            if "review" in c.lower()
        ]

        if review_columns:

            review_column = review_columns[0]

            st.subheader(
                "👤 Human Review Status"
            )

            st.bar_chart(
                evidence_df[review_column]
                .fillna("Unknown")
                .value_counts()
            )

    else:

        st.warning(
            "Evidence file not found."
        )


# ============================================================
# DELIVERY OUTPUT
# ============================================================

elif page == "📋 Delivery Output":

    st.header("📋 ProductIQ Final Delivery")

    st.write(
        "Final dataset prepared according to "
        "the required delivery format."
    )

    if total_columns == 252:

        st.success(
            "✅ 252-column expected delivery format detected."
        )

    else:

        st.warning(
            f"⚠️ Current dataset contains "
            f"{total_columns} columns."
        )

    st.metric(
        "Products in Final Delivery",
        f"{total_products:,}"
    )

    st.dataframe(
        df.head(50),
        use_container_width=True,
        height=500
    )

    st.divider()

    final_csv = (
        df.to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "⬇️ Download ProductIQ Final Delivery",
        final_csv,
        "ProductIQ_Final_Delivery.csv",
        "text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ProductIQ | AI-Powered Product Enrichment | Hackathon Demo"
)