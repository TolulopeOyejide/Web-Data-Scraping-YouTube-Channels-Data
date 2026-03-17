import os
from datetime import datetime

# --- SETTINGS ---
INPUT_FILE = "raw_youtube_usernames.txt"  # Put your filename here
OUTPUT_FILE = "youtube_usernames.txt"


def clean_text_file(input_path):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    # Read lines and strip whitespace
    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Remove duplicates by converting to a set, then sort alphabetically
    unique_sorted_lines = sorted(list(set(lines)))


    # Save the result
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in unique_sorted_lines:
            f.write(line + "\n")

    print(f"Done! Cleaned {len(lines)} lines down to {len(unique_sorted_lines)} unique records.")
    print(f"File saved to: {OUTPUT_FILE}")

# Run the function
clean_text_file(INPUT_FILE)