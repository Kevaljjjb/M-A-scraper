import pandas as pd

# Define the path to your CSV file and the Excel file
csv_file_path = 'Output.csv'
excel_file_path = 'Deal.xlsx'

# Read the CSV data into a DataFrame
csv_data = pd.read_csv(csv_file_path)

# Read the existing Excel data (if it exists) into a DataFrame
try:
    excel_data = pd.read_excel(excel_file_path)
except FileNotFoundError:
    # If the Excel file doesn't exist, create a new DataFrame
    excel_data = pd.DataFrame()

# Append the CSV data to the existing Excel data
combined_data = pd.concat([excel_data, csv_data], ignore_index=True)

# Convert the "Scraping Date" column to datetime without a time portion
combined_data['Scraping Date'] = pd.to_datetime(combined_data['Scraping Date'], format='%m-%d-%y').dt.date

# Sort the combined data by the "Scraping Date" column in reverse order
combined_data.sort_values(by='Scraping Date', ascending=False, inplace=True)

# Write the sorted data back to the Excel file in append mode
with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    combined_data.to_excel(writer, index=False, sheet_name='Sheet1')

print("Data appended and sorted in reverse order in the Excel file.")
