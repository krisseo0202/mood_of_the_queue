# Mood Tracker

A simple internal tool for tracking and visualizing moods using Streamlit and Google Sheets.

## Features

- Log moods with emoji selection
- Add short notes (max 50 words)
- Visualize daily mood distribution
- Store data in Google Sheets
- Filter by date

## Setup

1. Set up Google Sheets API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API and Google Drive API
   - Create a service account and download the credentials JSON file
   - Rename the downloaded file to `credentials.json` and place it in the project root directory
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Select your mood from the dropdown in the sidebar
2. Add a note (maximum 50 words)
3. Click "Log Mood" to save your entry
4. View the mood distribution chart and recent entries in the main area
