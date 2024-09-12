import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker

# Load the dataset from your CSV file
df = pd.read_csv('MAL_anime_details.csv')  # Load the CSV file

### Data Cleaning
# Remove "Genre: " prefix if it exists (adjust based on actual data)
df['Genres'] = df['Genres'].apply(lambda x: x.split(': ')[-1] if isinstance(x, str) else x)
df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce')
df['Ranked'] = pd.to_numeric(df['Ranked'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Aired'] = df['Aired'].fillna('')  # Fill NaN with empty string for easier processing

# Extract season and year from the 'Aired' field
def extract_season_year(aired_str):
    import re
    match = re.search(r'(\d{4})', aired_str)
    year = match.group(1) if match else 'Unknown'
    season = 'Unknown'
    if 'Winter' in aired_str:
        season = 'Winter'
    elif 'Spring' in aired_str:
        season = 'Spring'
    elif 'Summer' in aired_str:
        season = 'Summer'
    elif 'Fall' in aired_str:
        season = 'Fall'
    return pd.Series([season, year])

df[['Season', 'Year']] = df['Aired'].apply(extract_season_year)

# Create a PdfPages object to save multiple plots into a single PDF
with PdfPages('anime_report.pdf') as pdf:

    # Plot 1: Distribution of genres
    plt.figure(figsize=(15, 10))
    genre_join = ','.join(df['Genres'].dropna())  # Drop NaN values to avoid errors
    genre_split = genre_join.split(',')
    result = [x.strip() for x in genre_split]
    data = pd.Series(result)
    mydata = data.value_counts().tolist()  # List of genre counts
    labels = data.value_counts().index.tolist()  # List of genre labels
    newdf = pd.DataFrame({'Genre': labels, 'Total': mydata})
    sns.barplot(data=newdf, x='Total', y='Genre', palette='Spectral')
    plt.title('Distribution of Anime Genres on MAL')
    plt.xlabel('Total Number of Animes')
    plt.ylabel('Genre')
    pdf.savefig()
    plt.close()

    # Plot 2: Correlation between the number of episodes and rating
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='Episodes', y='Rating', data=df, color='orange', s=100, alpha=0.7)
    sns.regplot(x='Episodes', y='Rating', data=df, scatter=False, color='blue', line_kws={'linewidth':2})
    plt.title('Correlation between Number of Episodes and Rating')
    plt.xlabel('Number of Episodes')
    plt.ylabel('Rating')
    plt.xscale('log')  # Log scale for better visualization of large ranges
    plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
    plt.gca().xaxis.set_major_locator(ticker.LogLocator(base=10.0, subs='auto', numticks=10))
    plt.ylim(0, 10)  # Assuming ratings are on a scale from 0 to 10
    plt.grid(True)
    pdf.savefig()  # Save the current figure into the PDF
    plt.close()

    # Plot 3: Top 10 genres with the highest average ratings
    plt.figure(figsize=(12, 5))  # Adjusted height
    genre_rating = df.groupby('Genres')['Rating'].mean().sort_values(ascending=False)
    top_10_genres = genre_rating.head(10)
    sns.barplot(x=top_10_genres.index, y=top_10_genres.values, palette='viridis')
    plt.title('Top 10 Genres with the Highest Average Ratings')
    plt.xlabel('Genre')
    plt.ylabel('Average Rating')
    plt.xticks(rotation=10, ha='right')
    pdf.savefig()
    plt.close()

    # Plot 4: Seasonal Trends Analysis from the aired field
    plt.figure(figsize=(12, 6))
    seasonal_trends = df.groupby('Season').size().reindex(['Winter', 'Spring', 'Summer', 'Fall', 'Unknown'])
    sns.barplot(x=seasonal_trends.index, y=seasonal_trends.values, palette='cubehelix')
    plt.title('Number of Anime Released per Season')
    plt.xlabel('Season')
    plt.ylabel('Number of Anime')
    pdf.savefig()
    plt.close()

    # Plot 5: Type vs rating
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Type', y='Rating', data=df, palette='Set2')
    plt.title('Type vs Rating')
    plt.xlabel('Type')
    plt.ylabel('Rating')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 10)
    pdf.savefig()
    plt.close()

    # Plot 6: Streaming platform vs number of anime released
    plt.figure(figsize=(12, 6))
    streaming_counts = df['Streaming Platforms'].dropna().str.split(', ', expand=True).stack().value_counts()
    sns.barplot(x=streaming_counts.index, y=streaming_counts.values, palette='Paired')
    plt.title('Streaming Platform vs Number of Anime Released')
    plt.xlabel('Streaming Platform')
    plt.ylabel('Number of Anime')
    plt.xticks(rotation=30)
    pdf.savefig()
    plt.close()

print("Report generated and saved as anime_report.pdf.")
