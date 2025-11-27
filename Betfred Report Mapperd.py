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
    "Order Deadline": "deadline_date",
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
    "VISITORSEX": "auditor_gender",
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
    if isinstance(mapping, str):
        if mapping in row and pd.notna(row[mapping]):
            return str(row[mapping]).strip()
    return ""

# ============================================================
# STREAMLIT FILE UPLOADER
# ============================================================

uploaded_file = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

if uploaded_file is not None:

    # ============================================================
    # LOAD DATA
    # ============================================================

    df = pd.read_csv(uploaded_file, dtype=str).fillna("")

    # ============================================================
    # BUILD OUTPUT DATAFRAME
    # ============================================================

    final_df = pd.DataFrame()

    for report_col, export_mapping in COLUMN_MAP.items():
        final_df[report_col] = df.apply(lambda row: map_value(row, export_mapping), axis=1)

    # ============================================================
    # APPLY VALUE RENAMING
    # ============================================================

    col_challenge = "Were you challenged for ID on On entry/Whilst browsing, at the machine or after machine play?"
    if col_challenge in final_df.columns:
        final_df[col_challenge] = final_df[col_challenge].apply(
            lambda x: CHALLENGE_LOOKUP.get(str(x).strip().lower(), "")
            if pd.notna(x) else ""
        )

    col_betting = "ID'd on betting?"
    if col_betting in final_df.columns:
        final_df[col_betting] = final_df[col_betting].apply(
            lambda x: ID_BETTING_LOOKUP.get(str(x).strip().lower(), "")
            if pd.notna(x) else ""
        )

    # ============================================================
    # BLANK COLUMN HEADERS
    # ============================================================

    final_df.columns = ["" if col.startswith("blank") else col for col in final_df.columns]

    # ============================================================
    # SHOW PREVIEW
    # ============================================================

    st.subheader("Preview of Output")
    st.write(final_df)

    # ============================================================
    # PREPARE DOWNLOAD
    # ============================================================

    output_buffer = io.BytesIO()
    final_df.to_csv(output_buffer, index=False, encoding="utf-8-sig")
    output_buffer.seek(0)

    st.download_button(
        label="Download Betfred Report Data CSV",
        data=output_buffer,
        file_name="Betfred Report Data.csv",
        mime="text/csv"
    )
