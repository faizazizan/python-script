import pandas as pd
from difflib import SequenceMatcher

# Load the CSV files
sb404_path = r"C:\Users\status404.csv"
sb200_path = r"C:\Users\status-200.csv"

sb404_df = pd.read_csv(sb404_path)
sb200_df = pd.read_csv(sb200_path)

# Function to find the best match based on similarity
def find_best_match(target_url, possible_matches):
    best_match = None
    highest_similarity = 0.0
    for url in possible_matches:
        similarity = SequenceMatcher(None, target_url, url).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = url
    return best_match

# Dictionary to store the redirect mapping
redirect_mapping = {'404_URL': [], '200_URL': []}

# Find the best match for each 404 URL
for sb404_url in sb404_df['URL']:
    best_match = find_best_match(sb404_url, sb200_df['URL'])
    redirect_mapping['404_URL'].append(sb404_url)
    redirect_mapping['200_URL'].append(best_match)

# Convert the mapping to a DataFrame
redirect_df = pd.DataFrame(redirect_mapping)

# Save the redirect mapping to a new CSV file
output_path = r"C:\Users\xxx.csv"
redirect_df.to_csv(output_path, index=False)

print("Redirect mapping has been saved to:", output_path)
