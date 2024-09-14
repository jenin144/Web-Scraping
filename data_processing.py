import logging
from csv import QUOTE_MINIMAL
import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import time
from datetime import datetime 
import re

def clean_and_transform_MAL_data(df):
    """
    Function to clean and transform the scraped data.
    """
    # Normalize 'Ranked': extract numeric value if present
    df['Ranked'] = df['Ranked'].str.extract('(\d+)', expand=False).astype(float)
    
    # Convert 'Episodes' to numeric, coercing errors to NaN
    df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce')
    
    # Replace 'N/A', 'Unknown', and empty strings with NaN
    df.replace(['N/A', 'Unknown', ''], np.nan, inplace=True)

    # Drop rows with all NaN values
    df.dropna(how='all', inplace=True)


    # Combine fields for duplicates
    df.sort_values('Ranked', inplace=True)  # Ensure proper ordering by Ranked or another relevant column
    for title, group in df.groupby('Title'):
        if len(group) > 1:
            # Iterate over columns and combine fields if NaN in the first occurrence
            for col in df.columns:
                if col != 'Title':
                    first_idx = group.index[0]
                    # Fill the first occurrence with available values from subsequent duplicates
                    df.at[first_idx, col] = group[col].bfill().iloc[0]
    
    # Remove duplicates based on 'Title'
    df.drop_duplicates(subset=['Title'], inplace=True)

    # Reorder columns if needed
    df = df[['Title', 'English Name', 'Type', 'Episodes', 'Genres', 'Ranked', 'Aired', 'Streaming Platforms']]




#***********************************************
def clean_and_process_all_data(df):
    """
    Function to clean and transform the scraped data.
    """
    # Convert 'Episodes' to numeric, coercing errors to NaN
    df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce')
    
    # Replace 'N/A', 'Unknown', and empty strings with NaN
    df.replace(['N/A', 'Unknown', ''], np.nan, inplace=True)

    # Drop rows with all NaN values
    df.dropna(how='all', inplace=True)

     # Remove leading numbers followed by a period from 'Title'
    df['Title'] = df['Title'].apply(lambda x: re.sub(r'^\d+\.\s*', '', x) if pd.notna(x) else x)
    
    # Standardize 'Type' values
    df['Type'] = df['Type'].apply(lambda x: 'TV' if pd.notna(x) and 'TV' in x else x)
    

    # Standardize the aired field to a 'YYYY-YYYY' format
    def standardize_aired(aired_str):
        if pd.isna(aired_str):
            return aired_str
        match = re.search(r'(\d{4})\s*-\s*(\d{4})', aired_str)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        match = re.search(r'(\d{4})', aired_str)
        if match:
            return f"{match.group(1)}-{match.group(1)}"
        return aired_str

    if 'Aired' in df.columns:
        df['Aired'] = df['Aired'].apply(standardize_aired)

    # Combine rows with the same Title
    def combine_matching_anime(df):
        combined_rows = []
        to_drop = set()  # Set to keep track of indexes to drop

        for title, group in df.groupby('Title'):
            if len(group) > 1:  # Only combine if there are duplicates
                # Combine English names
                english_name = group['English Name'].dropna().unique()
                english_name = english_name[0] if len(english_name) > 0 else np.nan

                # Combine Types based on majority vote
                type_mode = group['Type'].mode()
                anime_type = type_mode[0] if not type_mode.empty else np.nan

                # Episodes (assuming all are the same or keep the first non-null)
                episodes = group['Episodes'].iloc[0]

                # Combine genres (join unique genres)
                genres = ', '.join(pd.Series(', '.join(group['Genres'].dropna()).split(', ')).unique())

                # Combine ranked (keep the first non-null)
                ranked = group['Ranked'].dropna().iloc[0] if not group['Ranked'].dropna().empty else np.nan

                # Combine aired date (take the first non-null)
                aired = group['Aired'].dropna().iloc[0] if not group['Aired'].dropna().empty else np.nan

                # Combine streaming platforms (join unique platforms)
                streaming_platforms = ', '.join(pd.Series(', '.join(group['Streaming Platforms'].dropna()).split(', ')).unique())

                # Convert ratings to numeric
                group['Rating'] = pd.to_numeric(group['Rating'], errors='coerce')
                ratings = group['Rating'].dropna()
                
                if len(ratings.unique()) == 1:  # If all ratings match
                    rating = ratings.iloc[0]
                else:  # Take average if there's no consensus
                    rating = round(ratings.mean(),2)

                # Append the combined row
                combined_rows.append({
                    'Title': title,
                    'English Name': english_name,
                    'Type': anime_type,
                    'Episodes': episodes,
                    'Genres': genres,
                    'Ranked': ranked,
                    'Aired': aired,
                    'Streaming Platforms': streaming_platforms,
                    'Rating': rating
                })

                # Add indexes to drop
                to_drop.update(group.index)
        
        # Create a DataFrame from combined rows
        combined_df = pd.DataFrame(combined_rows)
        
        # Drop combined rows from original DataFrame
        df_dropped = df.drop(index=to_drop)
        
        # Append combined rows to the remaining DataFrame
        final_df = pd.concat([df_dropped, combined_df], ignore_index=True)
        return final_df

    # Apply the combine function
    df = combine_matching_anime(df)

    # Reorder columns if needed
    df = df[['Title', 'English Name', 'Type', 'Episodes', 'Genres', 'Ranked', 'Aired', 'Streaming Platforms', 'Rating']]
    

        # Convert 'Rating' to numeric, coercing errors to NaN
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    # Sort by 'Rating' in descending order
    df.sort_values(by='Rating', ascending=False, inplace=True)


    return df

#***********************************************************
