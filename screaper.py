import threading
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import requests
from csv import QUOTE_MINIMAL
import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import time



# Configure logging to write logs to a file
logging.basicConfig(
    filename='anime_scraper.log',   # Log file name
    filemode='w',                   # Overwrite the file each time
    level=logging.INFO,             # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'     # Date format for the log
)

def scrape_anime_links(thread_id, url, anime_data_list):
    """
    Function to scrape anime links from a given MyAnimeList URL using Selenium WebDriver.
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode for better performance
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 5)

    logging.info(f"Thread {thread_id} starting scraping: {url}")

    try:
        # Load the page
        driver.get(url)

        # Wait for anime elements to be present and extract their links
        anime_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.ranking-list a[href*="/anime/"]'))
        )
        links = [
                element.get_attribute('href')
                for element in anime_elements
                if '/anime/' in element.get_attribute('href') and '/video' not in element.get_attribute('href') and 'add?selected_series_id' not in element.get_attribute('href')
            ]
        # Remove duplicates and limit to top 50
        links = list(dict.fromkeys(links))[:50]
        
        # Log each link being processed
        for link in links:
            logging.info(f"Processing: {link}")
            anime_details = get_anime_details(link)  # Fetch anime details
            anime_data_list.append(anime_details)  # Store in provided list

    except Exception as e:
        logging.error(f"Thread {thread_id} encountered an error: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Thread {thread_id} finished")

def get_anime_details(url):
    """
    Function to scrape anime details from a given anime URL using BeautifulSoup.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Finding the anime title
        title_element = soup.find('h1', class_='title-name h1_bold_none')
        title = title_element.string.strip() if title_element else 'N/A'

        # Finding the English name
        english_name_element = soup.find('span', class_='dark_text', string='English:')
        english_name = english_name_element.find_next_sibling(string=True).strip() if english_name_element else 'N/A'

        # Finding the synonyms
        synonyms_element = soup.find('span', class_='dark_text', string='Synonyms:')
        synonyms = synonyms_element.find_next_sibling(string=True).strip() if synonyms_element else 'N/A'

        # Finding the type
        type_element = soup.find('span', class_='dark_text', string='Type:')
        anime_type = type_element.find_next_sibling('a').text.strip() if type_element else 'N/A'

        # Finding the number of episodes
        episodes_element = soup.find('span', class_='dark_text', string='Episodes:')
        episodes = episodes_element.find_next_sibling(string=True).strip() if episodes_element else 'N/A'

        # Finding the genres
        genres_element = soup.find('span', class_='dark_text', string='Genres:')
        genres = ', '.join([a.text for a in genres_element.find_next_siblings('a')]) if genres_element else 'N/A'

        # Finding the ranking
        ranked_element = soup.find('span', class_='dark_text', string='Ranked:')
        ranked = ranked_element.find_next_sibling(string=True).strip() if ranked_element else 'N/A'

        # Finding the airing dates
        aired_element = soup.find('span', class_='dark_text', string='Aired:')
        aired = aired_element.find_next_sibling(string=True).strip() if aired_element else 'N/A'

        # Finding the streaming platforms
        streaming_platforms = []
        streaming_div = soup.find('div', class_='pb16 broadcasts')
        if streaming_div:
            platform_links = streaming_div.find_all('a', title=True)
            streaming_platforms = ', '.join([a['title'] for a in platform_links])
        streaming = streaming_platforms if streaming_platforms else 'N/A'

        return {
            'Title': title,
            'English Name': english_name,
            'Synonyms': synonyms,
            'Type': anime_type,
            'Episodes': episodes,
            'Genres': genres,
            'Ranked': ranked,
            'Aired': aired,
            'Streaming Platforms': streaming
        }

    except Exception as e:
        logging.error(f"Error while scraping {url}: {e}")
        return None


def scrap_500_mal(anime_data_all):
    count = 1  # Initialize the count

    # Define the maximum number of pages to scrape
    max_pages = 10 #90 

    for page in range(max_pages):
        animelisturl = f'https://myanimelist.net/topanime.php?limit={page * 50}'
        anime_data_page = scrape_myanimelist500(animelisturl, count)
        anime_data_all.extend(anime_data_page)
        count += len(anime_data_page)

    anime_data_all = [anime for anime in anime_data_all if any(anime.values())] 
    return  anime_data_all



def scrape_myanimelist500(url, start_count):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the anime containers
    anime_containers = soup.find_all('tr', class_='ranking-list')
  
    count = start_count
    anime_data = []

    for container in anime_containers:
        # Extract the title
        title_tag = container.find('h3', class_='anime_ranking_h3')
        title = title_tag.text.strip() if title_tag else 'N/A'

        # Extract the rating
        rating_tag = container.find('span', class_='score-label')
        rating = rating_tag.text.strip() if rating_tag else 'N/A'

        # Extract the number of episodes
        info_tag = container.find('div', class_='information')
        info = info_tag.get_text(strip=True) if info_tag else 'N/A'
        type = info.split(' ')[0] if 'eps' in info else 'N/A'
        ep = info.split(' ')[1] if 'eps' in info else 'N/A'
        if ep.startswith('('):
            episode = ep[1]
        else:
            episode = ep

        anime_data.append({
            'Ranked': count,
            'Title': title,
            'Rating': rating,
            'Episodes': episode,
            'Type': type
        })

        log_message = f'Rank: {count}, Title: {title}, Rating: {rating}, Episodes: {episode}, Type: {type}'
        logging.info(log_message)
        count += 1

    return anime_data  # Return the list of anime data dictionaries


def save_anime_details_to_csv(mal_data, IMDb_data,csv_filename):
    """
    Function to save anime details to a CSV file.
    """
    df = pd.DataFrame(mal_data)
    
    # Clean and transform data before saving
    clean_and_transform_MAL_data(df)

    df = df + IMDb_data    
    # Save the DataFrame to CSV with proper formatting
    df.to_csv(csv_filename, index=False, quoting=QUOTE_MINIMAL, escapechar='\\')

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
    df = df[['Title', 'English Name', 'Synonyms', 'Type', 'Episodes', 'Genres', 'Ranked', 'Aired', 'Streaming Platforms']]



def scrapIMDb(threadid ,imdb_list, url):
    options = Options()
    options.add_argument("--headless")  # Uncomment to run in headless mode
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    def extract_titles(existing_titles):
        new_titles = set()
        try:
            # Scroll down to load more content
            time.sleep(5)  # Allow time for content to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Allow more time for additional content to load

            # Extract titles
            titles = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/title/"]')
            for title in titles:
                title_text = title.text.strip()  # Remove extra spaces and newlines
                if title_text and title_text not in existing_titles:
                    new_titles.add(title_text)
                    # Log new titles to a file
                    logging.info(title_text)
                    # Append new titles to imdb_list
                    imdb_list.append(title_text)
                    
        except Exception as e:
            print(f"Failed to extract titles: {e}")
        return new_titles

    # Initialize sets to track titles
    all_titles = set()
    new_titles = extract_titles(all_titles)
    all_titles.update(new_titles)

    # Initialize the page counter
    page_count = 1
    max_pages = 5  

    # Loop to click "See More" button until the limit of pages is reached
    while page_count < max_pages:
        try:
            # Scroll down the page incrementally to bring the "See More" button into view
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)

            # Find the "See More" button
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "ipc-see-more__button")]'))
            )

            # Use JavaScript click to avoid move target issues
            driver.execute_script("arguments[0].click();", see_more_button)

            # Wait for new content to load
            time.sleep(5)

            # Extract titles from the current page
            new_titles = extract_titles(all_titles)
            all_titles.update(new_titles)

            # Increment the page counter
            page_count += 1

        except Exception as e:
            print(f"An error occurred or no more pages to load: {e}")
            break

    # Close the driver
    driver.quit()



def main():
    # URLs for scraping
    top_mal_url_1 = 'https://myanimelist.net/topanime.php'  # First URL to scrape
    top_mal_url_2 = 'https://myanimelist.net/topanime.php?limit=50'  # Second URL to 
    top_IMDb_url_1=  'https://www.imdb.com/search/title/?keywords=anime'


    # Separate lists to store anime data for each thread
    anime_data_thread1 = []
    anime_data_thread2 = []
    anime_data_thread4 = []
    anime_data_thread5 = []




    # Create threads for scraping
    thread1 = threading.Thread(target=scrape_anime_links, args=(1, top_mal_url_1, anime_data_thread1))   #MAL fisrt page 
    thread2 = threading.Thread(target=scrape_anime_links, args=(2, top_mal_url_2, anime_data_thread2))  # MAL second page
    thread4 = threading.Thread(target=scrap_500_mal, args=(anime_data_thread4,))   #MAL 4500 Anime 
    thread5 = threading.Thread(target=scrapIMDb, args=(5,anime_data_thread5,top_IMDb_url_1))




    #wait thread 4 to finish to start 1 & 2
    thread4.start()
    thread4.join()
    # Start 1 & 2 threads
    thread1.start()
    thread2.start()
#****
    # Wait for both threads to complete
    thread1.join()
    thread2.join()
#****
    thread5.start()
    thread5.join()

    # Combine data
    combined_mal_data = anime_data_thread1 + anime_data_thread2  + anime_data_thread4

    # Save the combined anime details to CSV
    save_anime_details_to_csv(combined_mal_data,anime_data_thread5, 'MAL_anime_details.csv')

    logging.info("Both threads have completed and data is saved to CSV.")

if __name__ == "__main__":
    main()





