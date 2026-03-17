import pandas as pd
import glob
from datetime import datetime

# Get a list of all CSV files in the current folder
files = glob.glob("*.csv")

# Load and combine them into one table
combined_data = pd.concat([pd.read_csv(f) for f in files])

# Remove duplicates based on the YouTube Channel Link column
combined_data = combined_data.drop_duplicates(subset=['YouTube Channel Link'], keep='first')

# Create a timestamp (Format: Year-Month-Day_Hour-Minute)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
output_filename = f"final_YT_channels_data_{timestamp}.csv"

# Save the result to the new file
combined_data.to_csv(output_filename, index=False)

print(f"Done! final_YT_channels_data {len(files)} files into {output_filename}")
print(f"Final unique record count: {len(combined_data)}")