import os
from datetime import datetime, date
import json
import tempfile
import gspread
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from google.oauth2.service_account import Credentials

EMOJIS = ['😍 (Happy)', '😐 (Neutral)', '😭 (Sad)', '😡 (Angry)', '😴 (Tired)', '😰 (Anxious)', '🤢 (Sick)', '😲 (Surprised)']
MOOD_MAP = {
    '😍 (Happy)': 'Happy',
    '😐 (Neutral)': 'Neutral',
    '😭 (Sad)': 'Sad',
    '😡 (Angry)': 'Angry',
    '😴 (Tired)': 'Tired',
    '😰 (Anxious)': 'Anxious',
    '🤢 (Sick)': 'Sick',
    '😲 (Surprised)': 'Surprised'
}
SHEET_ID = "173dOImclu9vOzDcBVBIJlivTt3efRYj4_zz3tm2_sUY"

def service_account_file_from_secrets(section="gcp_service_json"):
    sa_info = st.secrets[section]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(json.dumps(sa_info).encode())
    tmp.close()
    return tmp.name   

def get_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    json_file = service_account_file_from_secrets()
    creds = Credentials.from_service_account_info(json.loads(open(json_file).read()), scopes=scopes)
    return gspread.authorize(creds)


def get_sheet(gc):
    try:
        sh = gc.open_by_key(SHEET_ID)
        st.toast(f"Opened existing spreadsheet")
    except gspread.exceptions.SpreadsheetNotFound:
        st.toast(f"Spreadsheet not found")
        return None
    return sh


def log_mood(ws):
    with st.sidebar.form("log_form"):
        st.subheader("Log your mood")
        mood = st.selectbox("How are you feeling?", EMOJIS)
        note = st.text_area("Note (50 words max)", max_chars=250, help="Optional: Add a short note")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not note.strip():
                ws.append_row([ts, mood, ""])
                st.success("Submited!")
            elif len(note.split()) <= 50:
                ws.append_row([ts, mood, note.strip()])
                st.success("Submited!")
            else:
                st.warning("Please enter ≤ 50 words.")


def load_dataframe(ws):
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Timestamp", "Mood", "Note"])
    df = pd.DataFrame(data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Mood"] = df["Mood"].map(MOOD_MAP)
    return df


def plot_daily(df, date):
    day_df = df[df["Timestamp"].dt.date == date]
    if day_df.empty:
        st.info("No entries for this date.")
        return
    counts = day_df["Mood"].value_counts()
    fig, ax = plt.subplots()
    bars = ax.bar(counts.index, counts.values)
    ax.set_xticks(range(len(counts.index)))
    ax.set(title="Mood distribution", xlabel="Mood", ylabel="Count")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="Mood of the Queue", page_icon="🧪")
    st.title("Mood of the Queue")

    gc = get_client()
    sheet = get_sheet(gc)
    ws = sheet.sheet1

    log_mood(ws)
    df = load_dataframe(ws)
    if df.empty:
        st.info("No data yet – log your first mood!")
        return
    if "Timestamp" in df.columns and not df["Timestamp"].empty:
        min_d, max_d = df["Timestamp"].dt.date.min(), df["Timestamp"].dt.date.max()
        today = date.today()
        picked = st.sidebar.date_input("Pick a date", value=today, min_value=min_d, max_value=max_d)
        st.header(f"Mood stats for {picked}")
        plot_daily(df, picked)
    else:
        st.info("No timestamp data available for date selection.")


if __name__ == "__main__":
    main()
