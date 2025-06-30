import polars as pl
import os
from dotenv import load_dotenv
import re
from functools import lru_cache

load_dotenv()


@lru_cache(maxsize=1)  # Cache the result for better performance
def get_base_data():

    query = "SELECT * FROM mtss_base"
    assementQuery = "SELECT * FROM mtss_assessments"

    df = pl.read_database_uri(query=query, uri=os.getenv("DB_URL"))
    assesment_df = pl.read_database_uri(
        query=assementQuery, uri=os.getenv("DB_URL"))
    # fill nulls with empty strings
    assesment_df = assesment_df.fill_null("")
    pivoted = assesment_df.pivot(
        index='SSID',
        columns=['TEST_NAME', 'SUBJECT', 'SCHOOL_YEAR', 'TEST_DATE'],
        values=['PL', 'SS'],
        aggregate_function='first'
    )

    def clean_col(col):
        if isinstance(col, str) and '{' in col and '}' in col:
            # Extract the prefix (PL or SS)
            prefix, rest = col.split('_', 1)
            # Remove curly braces and quotes
            rest_clean = re.sub(r'[{}"]', '', rest)
            # Replace commas (delimiters from pivot) with spaces for readability
            rest_clean = rest_clean.replace(',', ' ')
            return f"{rest_clean} {prefix}"
        return str(col)
    pivoted.columns = [clean_col(col) for col in pivoted.columns]
    assem_data = pivoted
    # left join the df to dd on SSID
    dd = df.join(assem_data, on='SSID', how='left')
    g = get_grades()
    # left join the grades data on SSID
    dd = dd.join(g, on='SSID', how='left')
    # rename the column call ESL to Language
    dd = dd.rename({"ESL": "Language"})
    # make the return a lazy frame

    return dd


@lru_cache(maxsize=1)  # Cache the result for better performance
def get_grades():
    elQuery = '''select me.*
    from mtss_base mb 
    inner join mtss_elgrades me on me."SSID" = mb."SSID" '''
    secQuery = '''select ms.*
    from mtss_base mb 
    inner join mtss_segrades ms  on ms."SSID" = mb."SSID"'''

    df = pl.read_database_uri(query=elQuery, uri=os.getenv("DB_URL"))
    sec_df = pl.read_database_uri(query=secQuery, uri=os.getenv("DB_URL"))
    # combaine the two dataframes insert blank columns for the other
    df = df.join(sec_df, on='SSID', how='outer')
    # merge the SSID and SSID_right columns
    df = df.with_columns(
        pl.when(pl.col("SSID").is_null())
        .then(pl.col("SSID_right"))
        .otherwise(pl.col("SSID")).alias("SSID")
    )
    # drop the SSID_right column
    df = df.drop("SSID_right")
    df = df.fill_null("")

    # Rename columns according to mapping
    col_map = {
        'E': 'English',
        'M': 'Math',
        'R': 'Reading',
        'LW': 'LanguageWriting',
        'S': 'Science',
        'SS': 'SocialStudies',
        # 'GR', 'T', 'Q', 'S' are kept as is
    }

    def rename_col(col):
        # Only replace if the column matches exactly or as a suffix/prefix
        for k, v in col_map.items():
            # Replace only if the column is exactly k or starts/ends with k separated by _
            if col == k:
                return v
            # Replace _k_ with _v_, _k with _v, k_ with v_
            col = re.sub(rf'(?<=_)({k})(?=_)', v, col)
            col = re.sub(rf'^({k})(?=_)', v, col)
            col = re.sub(rf'(?<=_)({k})$', v, col)
        return col
    df.columns = [rename_col(col) for col in df.columns]

    return df


@lru_cache(maxsize=1)  # Cache the result for better performance
def casspp_data():

    query = "SELECT * FROM mtss_base"
    assementQuery = "SELECT * FROM mtss_assessments ms where ms.\"TEST_NAME\" = 'CAASPP' and ms.\"PL\" != '9'"

    df = pl.read_database_uri(query=query, uri=os.getenv("DB_URL"))
    assesment_df = pl.read_database_uri(
        query=assementQuery, uri=os.getenv("DB_URL"))
    # fill nulls with empty strings
    assesment_df = assesment_df.fill_null("")
    pivoted = assesment_df.pivot(
        index='SSID',
        columns=['TEST_NAME', 'SUBJECT', 'SCHOOL_YEAR', 'TEST_DATE'],
        values=['PL', 'SS'],
        aggregate_function='first'
    )
    # Rename the columns to a readable format with PL/SS at the end

    def clean_col(col):
        if isinstance(col, str) and '{' in col and '}' in col:
            # Extract the prefix (PL or SS)
            prefix, rest = col.split('_', 1)
            # Remove curly braces and quotes
            rest_clean = re.sub(r'[{}"]', '', rest)
            # Replace commas (delimiters from pivot) with spaces for readability
            rest_clean = rest_clean.replace(',', ' ')
            return f"{rest_clean} {prefix}"
        return str(col)
    pivoted.columns = [clean_col(col) for col in pivoted.columns]
    assem_data = pivoted
    # left join the df to dd on SSID
    dd = df.join(assem_data, on='SSID', how='left')
    dd = dd.rename({"ESL": "Language"})

    return dd


if __name__ == "__main__":
    print(get_grades())
