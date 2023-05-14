import json
import pandas as pd
import re
import os
from io import StringIO
from dotenv import load_dotenv
load_dotenv()
from github import Github

# Get our github api key from the file .env
# Then check login to github

personal_access_token = os.getenv('WAEL_PERSONAL_TOKEN')
# using an access token
g = Github(personal_access_token)

# Check that we can access the github api and returns correct user
try:   
    user = g.get_user()
    print(user.name)
except Exception as e:
    print(e)

# Read the Markdown file and extract the table as a string
with open('README.md', 'r') as f:
    markdown_text = f.read()

table_match = re.search(r'\|(.+)\|[\n|\r\n]\|(.+)\|[\n|\r\n](\|[-:| ]+\|[\n|\r\n])*((\|.+[\n|\r\n])+)', markdown_text)
table_text = table_match.group()

# Convert the table string to a pandas DataFrame and then to CSV
df = pd.read_csv(StringIO(table_text), sep='|', header=0, engine='python')

# Remove unnecessary columns with NaN values
df = df.drop(df.columns[[0,4]], axis=1)

# remove the beginning and ending spaces from the column names
df.columns = df.columns.str.strip()

# remove the beginning and ending spaces from the column values
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# drop the first row with the dashes/hyphens
df = df.drop(df.index[0])

# Only add the rows that have a value in their "Address" and "port" columns
current_df = pd.DataFrame()
for index, row in df.iterrows():
    if row['Address'].isspace() == False and row['Port'].isspace() == False:
        if row['Address'] != "" and row['Port'] != "":
            current_df = pd.concat([current_df, row.to_frame().transpose()])
            
# Upload the DataFrame as a Json file to the github repo
# Get the repo
repo = g.get_repo("armada-alliance/p2p-topo")

# Get the file
file = repo.get_contents("/p2p_Topo.json")

# Save the DataFrame to a Json file
json_data = current_df.to_json(orient='records')

# Check if the current content matches the new content
if file.decoded_content.decode("utf-8") != json_data:
    # Replace the file with the new JSON data
    repo.update_file(file.path, "Update p2p_Topo.json", json_data, file.sha)
    print("File updated successfully!")
else:
    print("No changes detected. File remains unchanged.")