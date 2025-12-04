import streamlit as st
import pandas as pd
import io

st.title("Betfred Weekly Report Mapper")

st.write("""
          1. Export the previous 2 weeks worth of Betfred AV data
          2. Drop the file in the box below – it’ll then give you the output file
          3. Standard bits - Check data vs previous week, remove data already reported, add new data
          4. Done.
          """)

# ============================================================
# COLUMN MAP
# ============================================================

COLUMN_MAP = {
    "Order Number": "order_internal_id",
    "Client Name": "client_name",
    "Visit Code": "internal_id",
    "Order Deadline": "site_internal_id",
    "Responsibility": "responsibility",
    "Premises Name": "site_name",
    "Address1": "site_address_1",
    "Address2": "site_address_2",
    "Address3": "site_address_3",
    "Post Code": "site_post_code",
    "Submitted": "submitted_date",
    "Approved": "approval_date",
    "Item to order": "item_to_order",
    "Actual Visit Date": "date_of_visit",
    "Actual Visit Time": "time_of_visit",
    "blank1": None,
    "Pass-Fail": "primary_result",
    "Pass-Fail2": "secondary_result",
    "Abort Reason": "Please detail why you were unable to conduct this audit:",
    "Extra Site 1": "site_code",
    "Extra Site 2": None,
    "Extra Site 3": None,
    "Extra Site 4": None,
    "Were you challenged for ID on On entry/Whilst browsing, at the machine or after machine play?": "Were you challenged for ID on entry, at the machine or after machine play?",
    "Machine play": None,
    "After machine": None,
    "ID'd on betting?": " Did the staff member who served you challenge you for ID at the counter while you placed your bet?",
    "blank2": None,
    "blank3": None,
    "VISITORSEX": None,
    "Eye contact on On entry/Whilst browsing": "As you entered the shop was eye contact made by a member of staff?",
    "Eye contact on betting": "Did the staff member who served you make eye contact with you?",
    "T21 cashier badge": None,
    "T21 posters shop": "Did you see any 'Think 21' posters in the shop?",
    "T21 posters Yes": "Did you see any 'Think 21' posters behind the counter?"
}

# ============================================================
# LOOKUP TABLES FOR VALUE RENAMING
# ============================================================

CHALLENGE_LOOKUP = {
    "entry": "On entry/Whilst browsing",
    "machine": "During machine play",
    "post_machine": "After machine play/Before reaching the counter",
    "not_challenged": "Not challenged here"
}

ID_BETTING_LOOKUP = {
    "not_challenged": "No",
    "counter": "Yes"
}

# ============================================================
# MAPPING FUNCTION
# ============================================================

def map_value(row, mapping):
    if mapping is None:
        return ""
    if isinstance(mapping, list):
        vals = []
        for col in mapping:
            if col in row and pd.notna(row[col]):
                cleaned = str(row[col]).strip()
                if cleaned:
                    vals.append(cleaned)
        return " | ".join(vals)
    if mapping in row and pd.notna(row[mapping]):
        return str(row[mapping]).strip()
    return ""

# ============================================================
# STREAMLIT UPLOADER
# ============================================================

uploaded_file = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file, dtype=str).fillna("")

    # Build initial mapped output
    mapped = pd.DataFrame()
    for report_col, source_col in COLUMN_MAP.items():
        mapped[report_col] = df.apply(lambda row: map_value(row, source_col), axis=1)

    # Apply lookup replacements
    col_challenge = "Were you challenged for ID on On entry/Whilst browsing, at the machine or after machine play?"
    if col_challenge in mapped.columns:
        mapped[col_challenge] = mapped[col_challenge].apply(
            lambda x: CHALLENGE_LOOKUP.get(str(x).strip().lower(), "") if pd.notna(x) else ""
        )

    col_betting = "ID'd on betting?"
    if col_betting in mapped.columns:
        mapped[col_betting] = mapped[col_betting].apply(
            lambda x: ID_BETTING_LOOKUP.get(str(x).strip().lower(), "") if pd.notna(x) else ""
        )

    # ============================================================
    # UNIQUE COLUMN NAMES FOR DISPLAY
    # ============================================================

    display_cols = []
    export_blanks = {}
    blank_counter = 1

    for col in mapped.columns:
        if col.startswith("blank"):
            display_col = f"_blank_{blank_counter}"
            export_blanks[display_col] = ""
            display_cols.append(display_col)
            blank_counter += 1
        else:
            display_cols.append(col)

    mapped.columns = display_cols

    # Display table safely
    st.subheader("Preview of Output")
    st.dataframe(mapped)

    # Convert back to true blank headers for export
    export_df = mapped.rename(columns=export_blanks)

    # Prepare CSV download
    buffer = io.BytesIO()
    export_df.to_csv(buffer, index=False, encoding="utf-8-sig")
    buffer.seek(0)

    st.download_button(
        label="Download Betfred Report Data CSV",
        data=buffer,
        file_name="Betfred Report Data.csv",
        mime="text/csv"
    )
