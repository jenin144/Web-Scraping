import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker

# Load the dataset from your CSV file


def plots():
    df = pd.read_csv('anime_details.csv')  # Load the CSV file
    ### Data Cleaning
    # Remove "Genre: " prefix if it exists (adjust based on actual data)
    df['Genres'] = df['Genres'].apply(lambda x: x.split(': ')[-1] if isinstance(x, str) else x)
    df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce')
    df['Ranked'] = pd.to_numeric(df['Ranked'], errors='coerce')
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Aired'] = df['Aired'].fillna('')  # Fill NaN with empty string for easier processing


    # Extract start year from 'Aired', handling invalid formats
    def extract_start_year(aired_str):
        if pd.isna(aired_str) or '-' not in aired_str:
            return pd.NA
        try:
            return int(aired_str.split('-')[0])
        except ValueError:
            return pd.NA

    # Create a PdfPages object to save multiple plots into a single PDF
    with PdfPages('plots.pdf') as pdf:

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



        # Plot 2: Average Rating by Genre
        plt.figure(figsize=(15, 10))
        df_genre = df.dropna(subset=['Genres'])
        df_genre = df_genre.assign(Genres=df_genre['Genres'].str.split(',')).explode('Genres')
        df_genre['Genres'] = df_genre['Genres'].astype(str).str.strip()
        genre_rating = df_genre.groupby('Genres')['Rating'].mean().reset_index()
        genre_rating.sort_values(by='Rating', ascending=False, inplace=True)
        sns.barplot(data=genre_rating, x='Rating', y='Genres', palette='Spectral')
        plt.title('Average Rating by Genre')
        plt.xlabel('Average Rating')
        plt.ylabel('Genre')
        pdf.savefig()
        plt.close()


        # Plot 3: Correlation between the number of episodes and rating
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


        # Plot 4: Average Rating by Type
        plt.figure(figsize=(15, 10))
        type_avg_rating = df.groupby('Type')['Rating'].mean().reset_index()
        type_avg_rating = type_avg_rating.sort_values(by='Rating', ascending=False)
        sns.barplot(data=type_avg_rating, x='Type', y='Rating', palette='Spectral')
        plt.title('Average Rating by Anime Type')
        plt.xlabel('Type')
        plt.ylabel('Average Rating')
        plt.xticks(rotation=45)  # Rotate x labels for better readability
        pdf.savefig()
        plt.close()

        # Plot 5: Streaming platform vs number of anime released
        plt.figure(figsize=(12, 6))
        streaming_counts = df['Streaming Platforms'].dropna().str.split(', ', expand=True).stack().value_counts()
        sns.barplot(x=streaming_counts.index, y=streaming_counts.values, palette='Paired')
        plt.title('Streaming Platform vs Number of Anime Released based on (100 anime)')
        plt.xlabel('Streaming Platform')
        plt.ylabel('Number of Anime')
        plt.xticks(rotation=45)
        pdf.savefig()
        plt.close()



        # Extract Start Year and calculate Number of Anime Released by Year
        df['Start Year'] = df['Aired'].apply(extract_start_year)
        df = df.dropna(subset=['Start Year'])
        df['Start Year'] = df['Start Year'].astype(int)
        anime_by_year = df['Start Year'].value_counts().sort_index()

        # Plot 6: Number of Anime Released by Year
        plt.figure(figsize=(12, 8))
        sns.barplot(x=anime_by_year.index, y=anime_by_year.values, palette='Paired')  # No hue, just palette
        plt.title('Number of Anime Released by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Anime')
        plt.xticks(rotation=45)
        pdf.savefig()
        plt.close()


    print("Report generated and saved as anime_report.pdf.")


      # Helper function to create and save tables with pagination
def create_table(pdf,dataframe, title, color1='#f5f5f5', color2='#ffcccc'):
    df = pd.read_csv('anime_details.csv')
    max_rows_per_page = 35 
    num_pages = (len(dataframe) + max_rows_per_page - 1) // max_rows_per_page
            
    for page in range(num_pages):
        start_row = page * max_rows_per_page
        end_row = min((page + 1) * max_rows_per_page, len(dataframe))
        page_df = dataframe.iloc[start_row:end_row]
                
        plt.figure(figsize=(12, 10))
        ax = plt.gca()
        ax.axis('off')
        table = plt.table(cellText=page_df.values,
                                  colLabels=page_df.columns,
                                  cellLoc='center',
                                  loc='center',
                                  cellColours=[[color1 if i % 2 == 0 else color2 for i in range(len(page_df.columns))] for _ in range(len(page_df))],
                                  colColours=[color1]*len(page_df.columns))
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.2)
        plt.title(f'{title} - Page {page + 1} of {num_pages}')
        pdf.savefig()
        plt.close()

def top_100():
    df = pd.read_csv('anime_details.csv')
    # Create a PdfPages object to save multiple tables into a single PDF
    with PdfPages('top100.pdf') as pdf:
        
        # Table 1: Top 100 Anime
        top_anime = df[['Title', 'Rating']].dropna()
        top_anime = top_anime.sort_values(by='Rating', ascending=False).head(100)
        create_table(pdf,top_anime, 'Top 100 Anime by Rating', color1='#f5f5f5', color2='#ffcccc')


        
    print("Tables generated and saved as top100.pdf.")


def top_by_genre():
    with PdfPages('top_anime_by_genre.pdf') as pdf:
        df = pd.read_csv('anime_details.csv')
        # Table 2: Top 100 Drama
        df_drama = df[df['Genres'].str.contains('Drama', na=False)]
        top_drama = df_drama[['Title', 'Rating']].dropna().sort_values(by='Rating', ascending=False).head(100)
        create_table(pdf,top_drama, 'Top 100 Drama by Rating', color1='#f5f5f5', color2='#ffcccc')

            # Table 3: Top 100 Action
        df_action = df[df['Genres'].str.contains('Action', na=False)]
        top_action = df_action[['Title', 'Rating']].dropna().sort_values(by='Rating', ascending=False).head(100)
        create_table(pdf,top_action, 'Top 100 Action by Rating', color1='#f5f5f5', color2='#ffcccc')

        # Table 4: Top 100 Slice of Life
        df_slice_of_life = df[df['Genres'].str.contains('Slice of Life', na=False)]
        top_slice_of_life = df_slice_of_life[['Title', 'Rating']].dropna().sort_values(by='Rating', ascending=False).head(100)
        create_table(pdf,top_slice_of_life, 'Top 100 Slice of Life by Rating', color1='#f5f5f5', color2='#ffcccc')

        print("Tables generated and saved as top_anime_by_genre.pdf.")


def still_straming():
    with PdfPages('still_streaming_anime.pdf') as pdf:
        df = pd.read_csv('anime_details.csv')
        # Table 5: Still Streaming Series
        current_year = pd.Timestamp.now().year
        df_still_streaming = df[df['Aired'].str.contains(str(current_year), na=False)]
        still_streaming = df_still_streaming[['Title', 'Aired']].dropna()
        create_table(pdf,still_streaming, 'Still Streaming Series', color1='#f5f5f5', color2='#ffcccc')

        print("Tables generated and saved as still_streaming_anime.pdf.")


#top_100()
#top_by_genre()
#plots()
#still_straming()
