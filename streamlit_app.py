"""
Sports Club Management - Streamlit Frontend
Run with:  streamlit run streamlit_app.py
Expects facilities.csv, fees.csv, members.csv in the same folder
(or upload them via the sidebar on first run).
"""

import pandas as pd
import streamlit as st
from datetime import date

st.set_page_config(page_title="Sports Club Management", layout="wide")

MEMBER_FILE = "members.csv"
FEE_FILE = "fees.csv"
FACILITY_FILE = "facilities.csv"

MEMBER_COLS = [
    "MemberCode", "MemberName", "DateOfJoining", "Address",
    "PhoneNumber", "FacilityCode1", "FacilityCode2", "FacilityCode3",
    "NoOfChildren"
]
FEE_COLS = ["MemberCode", "DateOfSubmission", "Amount"]
FACILITY_COLS = ["FacilityCode", "Facility"]


# ---------- Data helpers ----------
def load_csv(path, cols):
    try:
        return pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        return pd.DataFrame(columns=cols)


def save_csv(df, path):
    df.to_csv(path, index=False)


def get_members():
    return load_csv(MEMBER_FILE, MEMBER_COLS)


def get_fees():
    return load_csv(FEE_FILE, FEE_COLS)


def get_facilities():
    return load_csv(FACILITY_FILE, FACILITY_COLS)


# ---------- Sidebar navigation ----------
st.sidebar.title("🏆 Sports Club Management")
section = st.sidebar.radio(
    "Go to",
    ["Members", "Fees", "Facilities", "Reports"]
)

# =====================================================================
# MEMBERS
# =====================================================================
if section == "Members":
    st.header("Member Processing")
    tab_view, tab_add, tab_edit, tab_delete = st.tabs(
        ["View", "Add", "Modify", "Delete"]
    )

    with tab_view:
        df = get_members()
        st.dataframe(df, use_container_width=True)

    with tab_add:
        facilities_df = get_facilities()
        fac_options = [""] + facilities_df["FacilityCode"].tolist() if not facilities_df.empty else [""]

        with st.form("add_member_form", clear_on_submit=True):
            code = st.text_input("Member Code")
            name = st.text_input("Name")
            doj = st.date_input("Date of Joining", value=date.today())
            address = st.text_input("Address")
            phone = st.text_input("Phone Number")
            c1, c2, c3 = st.columns(3)
            f1 = c1.selectbox("Facility Code 1", fac_options)
            f2 = c2.selectbox("Facility Code 2", fac_options)
            f3 = c3.selectbox("Facility Code 3", fac_options)
            noc = st.number_input("No. of Children", min_value=0, step=1)
            submitted = st.form_submit_button("Add Member")

            if submitted:
                df = get_members()
                if code.strip() == "":
                    st.error("Member Code is required.")
                elif code in df["MemberCode"].values:
                    st.error("A member with this code already exists.")
                else:
                    new_row = {
                        "MemberCode": code, "MemberName": name,
                        "DateOfJoining": doj.strftime("%d/%m/%Y"),
                        "Address": address, "PhoneNumber": phone,
                        "FacilityCode1": f1, "FacilityCode2": f2,
                        "FacilityCode3": f3, "NoOfChildren": noc
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(df, MEMBER_FILE)
                    st.success(f"Member {code} added.")

    with tab_edit:
        df = get_members()
        if df.empty:
            st.info("No members found.")
        else:
            code = st.selectbox("Select Member Code", df["MemberCode"].tolist())
            row = df[df["MemberCode"] == code].iloc[0]
            with st.form("edit_member_form"):
                name = st.text_input("Name", value=row["MemberName"])
                doj = st.text_input("Date of Joining (dd/mm/yyyy)", value=row["DateOfJoining"])
                address = st.text_input("Address", value=row["Address"])
                phone = st.text_input("Phone Number", value=row["PhoneNumber"])
                f1 = st.text_input("Facility Code 1", value=row["FacilityCode1"])
                f2 = st.text_input("Facility Code 2", value=row["FacilityCode2"])
                f3 = st.text_input("Facility Code 3", value=row["FacilityCode3"])
                noc = st.text_input("No. of Children", value=row["NoOfChildren"])
                submitted = st.form_submit_button("Save Changes")

                if submitted:
                    idx = df[df["MemberCode"] == code].index[0]
                    df.at[idx, "MemberName"] = name
                    df.at[idx, "DateOfJoining"] = doj
                    df.at[idx, "Address"] = address
                    df.at[idx, "PhoneNumber"] = phone
                    df.at[idx, "FacilityCode1"] = f1
                    df.at[idx, "FacilityCode2"] = f2
                    df.at[idx, "FacilityCode3"] = f3
                    df.at[idx, "NoOfChildren"] = noc
                    save_csv(df, MEMBER_FILE)
                    st.success("Member updated.")

    with tab_delete:
        df = get_members()
        if df.empty:
            st.info("No members found.")
        else:
            code = st.selectbox("Select Member Code to delete", df["MemberCode"].tolist(), key="del_member")
            st.write(df[df["MemberCode"] == code])
            if st.button("Delete Member", type="primary"):
                df = df[df["MemberCode"] != code]
                save_csv(df, MEMBER_FILE)
                st.success(f"Member {code} deleted.")
                st.rerun()

# =====================================================================
# FEES
# =====================================================================
elif section == "Fees":
    st.header("Fee Processing")
    tab_view, tab_add = st.tabs(["View", "Add"])

    with tab_view:
        st.dataframe(get_fees(), use_container_width=True)

    with tab_add:
        members_df = get_members()
        member_options = members_df["MemberCode"].tolist() if not members_df.empty else []
        with st.form("add_fee_form", clear_on_submit=True):
            code = st.selectbox("Member Code", member_options) if member_options else st.text_input("Member Code")
            fee_date = st.date_input("Fee Submission Date", value=date.today())
            amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
            submitted = st.form_submit_button("Record Fee")

            if submitted:
                df = get_fees()
                new_row = {
                    "MemberCode": code,
                    "DateOfSubmission": fee_date.strftime("%d/%m/%Y"),
                    "Amount": amount
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_csv(df, FEE_FILE)
                st.success("Fee recorded.")

# =====================================================================
# FACILITIES
# =====================================================================
elif section == "Facilities":
    st.header("Facility Processing")
    tab_view, tab_add = st.tabs(["View", "Add"])

    with tab_view:
        st.dataframe(get_facilities(), use_container_width=True)

    with tab_add:
        with st.form("add_facility_form", clear_on_submit=True):
            code = st.text_input("Facility Code")
            name = st.text_input("Facility Name")
            submitted = st.form_submit_button("Add Facility")

            if submitted:
                df = get_facilities()
                if code.strip() == "":
                    st.error("Facility Code is required.")
                elif code in df["FacilityCode"].values:
                    st.error("Facility already exists.")
                else:
                    new_row = {"FacilityCode": code, "Facility": name}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(df, FACILITY_FILE)
                    st.success("Facility added.")

# =====================================================================
# REPORTS
# =====================================================================
elif section == "Reports":
    st.header("Reporting")
    report = st.selectbox(
        "Choose a report",
        ["Member Details", "Activity Details", "Datewise Fee Details",
         "Overdue Fee Details", "Membership Card"]
    )

    if report == "Member Details":
        st.dataframe(get_members(), use_container_width=True)

    elif report == "Activity Details":
        members = get_members()
        facilities = get_facilities()
        if members.empty or facilities.empty:
            st.info("Members or facilities data missing.")
        else:
            for _, frow in facilities.iterrows():
                fcode, fname = frow["FacilityCode"], frow["Facility"]
                matched = members[
                    (members["FacilityCode1"] == fcode) |
                    (members["FacilityCode2"] == fcode) |
                    (members["FacilityCode3"] == fcode)
                ]
                st.subheader(f"Activity: {fname}")
                st.dataframe(matched[["MemberCode", "MemberName"]], use_container_width=True)

    elif report == "Datewise Fee Details":
        fees = get_fees()
        members = get_members()
        if fees.empty:
            st.info("No fee records found.")
        else:
            merged = fees.merge(members[["MemberCode", "MemberName"]], on="MemberCode", how="left")
            merged["_sort"] = pd.to_datetime(merged["DateOfSubmission"], format="%d/%m/%Y", errors="coerce")
            merged = merged.sort_values("_sort").drop(columns="_sort")
            st.dataframe(
                merged[["DateOfSubmission", "MemberCode", "MemberName", "Amount"]],
                use_container_width=True
            )

    elif report == "Overdue Fee Details":
        fees = get_fees()
        members = get_members()
        if fees.empty:
            st.info("No fee records found.")
        else:
            f = fees.copy()
            f["_date"] = pd.to_datetime(f["DateOfSubmission"], format="%d/%m/%Y", errors="coerce")
            f = f.dropna(subset=["_date"])
            latest = f.sort_values("_date").drop_duplicates("MemberCode", keep="last")
            cutoff = pd.Timestamp(date.today()) - pd.DateOffset(months=6)
            overdue = latest[latest["_date"] < cutoff]
            overdue = overdue.merge(members, on="MemberCode", how="left")
            st.dataframe(
                overdue[["MemberCode", "MemberName", "DateOfSubmission"]],
                use_container_width=True
            )

    elif report == "Membership Card":
        members = get_members()
        if members.empty:
            st.info("No members found.")
        else:
            code = st.selectbox("Select Member Code", members["MemberCode"].tolist())
            m = members[members["MemberCode"] == code].iloc[0]
            st.subheader("Membership Card")
            st.markdown(f"""
            | Field | Value |
            |---|---|
            | Member Code | {m['MemberCode']} |
            | Name | {m['MemberName']} |
            | Address | {m['Address']} |
            | Phone | {m['PhoneNumber']} |
            | Facilities | {m['FacilityCode1']}, {m['FacilityCode2']}, {m['FacilityCode3']} |
            | No. of Children | {m['NoOfChildren']} |
            | Date of Joining | {m['DateOfJoining']} |
            """)
            st.caption("This card is valid for 2 years from date of joining.")
