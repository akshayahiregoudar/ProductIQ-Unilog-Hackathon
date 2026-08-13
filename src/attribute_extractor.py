import pandas as pd
import re

# Load the dataset
file_path = "data/Unihack_ Sample Dataset - Input.csv"
df = pd.read_csv(file_path)


def extract_voltage(text):
    text = str(text)

    match = re.search(r'(\d+(?:\.\d+)?)\s*[Vv]\b', text)

    if match:
        return match.group(1) + " V"

    return None


def extract_amperage(text):
    text = str(text)

    match = re.search(r'(\d+(?:\.\d+)?)\s*[Aa]\b', text)

    if match:
        return match.group(1) + " A"

    return None


def extract_sound_level(text):
    text = str(text)

    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:dBA|DBA|dba)\b', text)

    if match:
        return match.group(1) + " dBA"

    return None


# Combine part description and manufacturer information
df["Search_Text"] = (
    df["Part_Desc"].fillna("").astype(str)
    + " "
    + df["Part_Manuf"].fillna("").astype(str)
)

# Extract attributes
df["Voltage"] = df["Search_Text"].apply(extract_voltage)
df["Amperage"] = df["Search_Text"].apply(extract_amperage)
df["Sound_Level"] = df["Search_Text"].apply(extract_sound_level)


print("===== ATTRIBUTE EXTRACTION =====")

print(
    df[
        [
            "Mfg_Part_Num",
            "Part_Desc",
            "Voltage",
            "Amperage",
            "Sound_Level"
        ]
    ].head(20).to_string(index=False)
)


print("\n===== EXTRACTION SUMMARY =====")

print("Voltage found:", df["Voltage"].notna().sum())
print("Amperage found:", df["Amperage"].notna().sum())
print("Sound level found:", df["Sound_Level"].notna().sum())