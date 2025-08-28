import pandas as pd
import re

# Load dataset
df = pd.read_excel("messy_IMDB_dataset.xlsx")
print(df.head())

# Split the single column into multiple columns
df = df.iloc[:,0].str.split(";", expand=True)

# Convert column names to strings
df.columns = df.columns.astype(str)

# Drop completely empty columns (see double ;; following Director column)
df = df.loc[:, (df != "").any(axis=0)]
print(df.head())

# Rename columns
df.columns = [
    "ID", "title", "release_yr", "genre",
    "duration", "country", "content_rating", "director",
    "income", "votes", "score"
]

# Print rows with at least one NaN
rows_with_na = df[df.isna().any(axis=1)]

print(rows_with_na)

# Fix datetime format (yyyy-mm-dd)
import re

def clean_date(date_str):
    if pd.isna(date_str):
        return None
    
    s = str(date_str).strip()
    s = re.sub(r"[-]+", "-", s)        # replace multiple dashes
    s = re.sub(r"\s+", " ", s)         # replace multiple spaces
    
    try:
        # Try default flexible parser
        return pd.to_datetime(s, errors="raise", dayfirst=True)
    except:
        # Try month-day-year (e.g. "09 21 1972")
        try:
            return pd.to_datetime(s, format="%m %d %Y", errors="raise")
        except:
            return None

# Apply parsing
parsed_dates = df["release_yr"].apply(clean_date)

# Create new columns:
df["release_parsed"] = parsed_dates.dt.strftime("%Y-%m-%d")
df["release_flag"]   = parsed_dates.isna()  # True = parsing failed

# Show flagged rows
flagged = df[df["release_flag"]]
print(flagged[["title", "release_yr"]])

# Cross-check - web search
# Manually fix specific rows by index
df.loc[70, "release_parsed"] = "1951-03-06"  # "The 6th of marzo, year 1951"
df.loc[83, "release_parsed"] = "1984-02-24"  # corrected invalid day
df.loc[84, "release_parsed"] = "1976-12-24"  # corrected invalid month/day

# Remove empty title/release_yr row 13
df = df[df["release_yr"].str.strip() != ""] 

# Update the flag column after manual fixes
df["release_flag"] = df["release_parsed"].isna()

# Replace original column with cleaned dates
df["release_yr"] = df["release_parsed"]

# Drop helper column
df = df.drop(columns=["release_parsed"])
df = df.drop(columns=['release_flag'])

print(df.head())

# Fix numeric columns
# Remove $ and non-numeric characters
df["income"] = df["income"].astype(str).str.replace(r"[^\d.]", "", regex=True)
df["income"] = pd.to_numeric(df["income"], errors="coerce")

# Remove dots, commas, non-numeric
df["votes"] = df["votes"].astype(str).str.replace(r"[^\d]", "", regex=True)
df["votes"] = pd.to_numeric(df["votes"], errors="coerce")

# Clean score column (replace comma or letter mistakes with dot)
df["score"] = df["score"].astype(str).str.replace(",", ".", regex=False)  # replace commas with dot
df["score"] = df["score"].str.extract(r"(\d+\.?\d*)")  # keep only numbers
df["score"] = pd.to_numeric(df["score"], errors="coerce")

# Check the cleaned data
print(df[["income", "votes", "score"]].head())

# Highest grossing movie
top_movie = df.loc[df['income'].idxmax()]
print(top_movie) # Endgame

# Top 3 highest grossing movies
top_3 = df.sort_values(by="income", ascending=False).head(3)

print(top_3)