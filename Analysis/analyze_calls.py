import os
import pandas as pd
import re
from pathlib import Path

CALLS_FOLDER = Path("D:/Data-Science-Basics/jupyterNotebook/QA-Calls-Review-Analysis/Automation/ssb_logs")

def extract_option(line):
    match = re.search(r"\]\s*(.*)", line)   #regex to extract text after '] '
    if match:
        return match.group(1)
    else:
        return None

def load_calls(folder_path):
    data = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if not lines:
                    continue
                last_line = lines[-2]   #bcz last line is \n
                option = extract_option(last_line)

                data.append({
                    'file_name': file.strip(".txt"),
                    'extracted_option': option
                })    
    return pd.DataFrame(data)

def generate_insight(statement,value,file_name="insights.txt",clear_File=False):
    if clear_File:
        # Clear file first time only
        open(file_name, "w").close()

    with open(file_name, 'a') as f:
        f.write(f"{statement} {value}\n")

def count_calls(calls_df):
    generate_insight("Total Calls Reviewed = ", len(calls_df), "insights.txt", True)

def categorize_options_and_find_success(calls_df):
    VISIT_CATEGORIES = {
    "Specific appointment or walk-in time / range within 1 hour" : "successful appointment",
    "Unscheduled walk-in or loose appointment time / range exceeding 1 hour": "successful appointment",
    "Appointment requested/mentioned but not set": "unsuccessful appointment",
    "No appointment, walk-in, or drop-off discussed": "unsuccessful appointment",
    "Upcoming scheduled appointment": "successful appointment",
    "Vehicle already in service": "in progress",
    "Not an appointment opportunity": "unsuccessful appointment",
    "Correction: caller never connected to a live, qualified agent": "unsuccessful appointment",
    "Unfamiliar Language": "unable to classify"
    }
    calls_df['conclusion'] = calls_df['extracted_option'].map(VISIT_CATEGORIES)
    category_counts = calls_df['conclusion'].value_counts()
    counts_dict = category_counts.to_dict()
    generate_insight("Appointments Conclusion:-\n",counts_dict)

    total_calls = len(calls_df)
    successful_appointments = category_counts.get("successful appointment", 0)
    success_percentage =(successful_appointments / total_calls) * 100
    generate_insight("Successful Rate of Booking New Appointments = ", f"{success_percentage:.2f}%")

def main():
    calls_df = load_calls(CALLS_FOLDER)
    calls_df.index = range(1, len(calls_df) + 1)
    calls_df.to_csv("calls_summary.csv", index_label="S.No")
    count_calls(calls_df)
    categorize_options_and_find_success(calls_df)

if __name__ == "__main__":
    main()