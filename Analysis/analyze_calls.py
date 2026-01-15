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

def main():
    calls_df = load_calls(CALLS_FOLDER)
    calls_df.index = range(1, len(calls_df) + 1)
    calls_df.to_csv("calls_summary.csv", index_label="S.No")
    print(len(calls_df))

if __name__ == "__main__":
    main()