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
from datetime import datetime 
import re
from data_processing import clean_and_process_all_data as clean_all
from data_processing import clean_and_transform_MAL_data as clean_mal


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
        links = list(dict.fromkeys(links))[:50] ####################################
        
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


def scrap_5000_mal(anime_data_all):
    count = 1  

    max_pages = 90 #90###########################################

    for page in range(max_pages):
        animelisturl = f'https://myanimelist.net/topanime.php?limit={page * 50}'
        anime_data_page = scrape_myanimelist5000(animelisturl, count)
        anime_data_all.extend(anime_data_page)
        count += len(anime_data_page)

    anime_data_all = [anime for anime in anime_data_all if any(anime.values())] 
    return  anime_data_all



def scrape_myanimelist5000(url, start_count):
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
        info_lines = info_tag.get_text(strip=True, separator='\n').split('\n') if info_tag else ['N/A', 'N/A', 'N/A']
        type_and_episodes = info_lines[0] if len(info_lines) > 0 else 'N/A'
        type = type_and_episodes.split(' ')[0] if 'eps' in type_and_episodes else 'N/A'
        ep = type_and_episodes.split(' ')[1] if 'eps' in type_and_episodes else 'N/A'
        if ep.startswith('('):
            episode = ep[1]
        else:
            episode = ep

        date_range = info_lines[1] if len(info_lines) > 1 else 'N/A'
    

        anime_data.append({
            'Ranked': count,
            'Title': title,
            'Rating': rating,
            'Episodes': episode,
            'Type': type,
            'Aired': date_range
        })

        log_message = f'Rank: {count}, Title: {title}, Rating: {rating}, Episodes: {episode}, Type: {type} , Aired: {date_range}'
        logging.info(log_message)
        count += 1

    return anime_data  # Return the list of anime data dictionaries


def save_anime_details_to_csv(mal_data, IMDb_data,AniList_data,csv_filename):
    """
    Function to save anime details to a CSV file.
    """
    df = pd.DataFrame(mal_data)
    
    # Clean and transform data before saving
    clean_mal(df)

    # Convert IMDb_data list to DataFrame
    imdb_df = pd.DataFrame(IMDb_data, columns=['Title', 'Rating', 'Aired'])
    
    # Convert AniList_data list to DataFrame
    AniList_df = pd.DataFrame(AniList_data, columns=['Title', 'Genres', 'Type', 'Episodes', 'Rating', 'Aired'])
    
    # Combine DataFrames
    combined_df = pd.concat([df, imdb_df, AniList_df], ignore_index=True)


    cleaned_df = clean_all(combined_df)

    # Save the DataFrame to CSV with proper formatting
    cleaned_df.to_csv(csv_filename, index=False, quoting=QUOTE_MINIMAL, escapechar='\\')


def scrapIMDb(threadid ,imdb_list, url):
    options = Options()
    options.add_argument("--headless")  # Uncomment to run in headless mode
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    def extract(existing_titles):
        new_titles = set()
        try:
            # Scroll down to load more content
            time.sleep(3)  # Allow time for content to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow more time for additional content to load

    # Extract titles, ratings, and date ranges
            anime_blocks = driver.find_elements(By.CLASS_NAME, 'sc-b189961a-0')  # Adjusted to locate the correct parent block
            for block in anime_blocks:
                try:
                    # Extract the title
                    title_element = block.find_element(By.CLASS_NAME, 'ipc-title-link-wrapper')
                    title_text = title_element.find_element(By.TAG_NAME, 'h3').text.strip()

                    # Extract the rating
                    try:
                        rating_element = block.find_element(By.CLASS_NAME, 'ipc-rating-star--rating')
                        rating_text = rating_element.text.strip()
                    except:
                        rating_text = "N/A"  # If rating is not available

                    # Extract the date range
                    try:
                        date_element = block.find_element(By.CLASS_NAME, 'sc-b189961a-8')  # Date range element
                        date_text = date_element.text.strip()
                    except:
                        date_text = "N/A"  # If date is not available

                    # Check if the title is new and log it
                    if title_text and title_text not in existing_titles:
                        new_titles.add(title_text)
                        imdb_list.append((title_text, rating_text, date_text))  # Append title, rating, and date as a tuple
                        logging.info(f"IMDb {title_text} - Rating: {rating_text} - Date Range: {date_text}")  # Log new titles, ratings, and dates

                except Exception as e:
                    print(f"Failed to extract title, rating, or date from block: {e}")

        except Exception as e:
            print(f"Failed to extract titles, ratings, and dates: {e}")
        return new_titles

    # Initialize sets to track titles
    all_titles = set()
    new_titles = extract(all_titles)
    all_titles.update(new_titles)

    page_count = 1
    max_pages =  6  #1 # 300#################################################3
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
            time.sleep(3)

            # Extract titles, ratings, and dates from the current page
            new_titles = extract(all_titles)
            all_titles.update(new_titles)


            # Increment the page counter
            page_count += 1

        except Exception as e:
            print(f"An error occurred or no more pages to load: {e}")
            break

    # Close the driver
    driver.quit()

def scrapAnilist (anilist,url):
    # Set up Firefox options
    options = Options()
    options.headless = True  # Run in headless mode (no GUI)
    options.add_argument("--headless")  # Uncomment to run in headless mode
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    max_anime = 1600 ###################################################

    try:
        # Wait for the button to be clickable and click it
        wait = WebDriverWait(driver, 5)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[data-icon="th-list"]')))
        button.click()
        # Wait for the page to update
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.title-link.ellipsis')))
        
        # Initialize variables for scrolling and counting titles
   
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while len(anilist) < max_anime:  # Limit to top 100 anime
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract anime titles using the provided CSS selector
            current_titles = [a.get_text(strip=True) for a in soup.select('a.title-link.ellipsis')]
            
            # Extract genres for each anime
            genre_elements = soup.select('div.genres')
            current_genres = []
            for genre_div in genre_elements:
                genres = [a.get_text(strip=True) for a in genre_div.select('a.genre')]
                current_genres.append(", ".join(genres))
            
            # Extract type and number of episodes for each anime
            type_elements = soup.select('div.row.format')
            current_types = []
            current_episodes = []
            for type_div in type_elements:
                # Extract type (e.g., "TV Show")
                anime_type = type_div.contents[0].strip()  # Get the first child and strip whitespace
                current_types.append(anime_type)
                
                # Extract number of episodes if available
                episodes_div = type_div.find('div', class_='sub-row length')
                if episodes_div:
                    episodes_text = episodes_div.get_text(strip=True)
                    if "episodes" in episodes_text:
                        episodes = episodes_text.split()[0]  # Extract the number part only
                    else:
                        episodes = 1  # Handle missing or unknown values
                else:
                    episodes = 1
                current_episodes.append(episodes)
            
            # Extract rating for each anime
            rating_elements = soup.select('div.percentage')
            current_ratings = []
            for rating_div in rating_elements:
                rating_text = rating_div.get_text(strip=True).split('%')[0]  # Extract percentage part only
                try:
                    rating_out_of_10 = round(float(rating_text) / 10, 1)  # Convert to scale out of 10
                except ValueError:
                    rating_out_of_10 = "Unknown"
                current_ratings.append(rating_out_of_10)
            
    #       Extract aired year for each anime
            aired_elements = soup.select('div.row.date')
            current_aired_years = []
            current_year = datetime.now().year  # Get the current year
            for aired_div in aired_elements:
                aired_text = aired_div.contents[0].strip()  # Get the first child and strip whitespace
                if "Airing" in aired_text:
                    year = str(current_year)  # Use the current year if "Airing"
                else:
                    year = aired_text.split()[-1] if aired_text.split()[-1].isdigit() else "Unknown"
                current_aired_years.append(year)
            
            # Append extracted details to the anilist and log each
            for title, genres, anime_type, episodes, rating, aired_year in zip(
                current_titles, current_genres, current_types, current_episodes, current_ratings, current_aired_years
            ):
                anime_details = {
                    "Title": title,
                    "Genres": genres,
                    "Type": anime_type,
                    "Episodes": episodes,
                    "Rating": rating,
                    "Aired": aired_year
                }
                anilist.append(anime_details)
                logging.info(f"Anillist : Title: {title} - Genres: {genres} - Type: {anime_type} - Episodes: {episodes} - Rating: {rating} - Aired Year: {aired_year}")
            
            
            # Scroll down to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for new content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        # Close the WebDriver
        driver.quit()
    return anilist


def main():
    # URLs for scraping
    top_mal_url_1 = 'https://myanimelist.net/topanime.php'  
    top_mal_url_2 = 'https://myanimelist.net/topanime.php?limit=50'  
    top_IMDb_url_1=  'https://www.imdb.com/search/title/?keywords=anime'
    top_AniList_url = 'https://anilist.co/search/anime/top-100?fbclid=IwY2xjawFRFxJleHRuA2FlbQIxMAABHWgq5I0pDoFJzDLBpaQNpx9NMS0Yqp1xUfHruU8WsMYAgL0X_cBWFGNnXQ_aem_xw299XsavXYX8I7Kki8UrA'

    # Separate lists to store anime data for each thread
    anime_data_thread1 = [] # My anime list data 
    anime_data_thread2 = []
    anime_data_thread4 = []
    anime_data_thread5 = [] # imdb data 
    anime_data_thread6 = [] # AniList data


    # Create threads for scraping
    thread1 = threading.Thread(target=scrape_anime_links, args=(1, top_mal_url_1, anime_data_thread1))   #MAL fisrt page 
    thread2 = threading.Thread(target=scrape_anime_links, args=(2, top_mal_url_2, anime_data_thread2))  # MAL second page
    thread4 = threading.Thread(target=scrap_5000_mal, args=(anime_data_thread4,))   #MAL 4500 Anime 
    thread5 = threading.Thread(target=scrapIMDb, args=(5,anime_data_thread5,top_IMDb_url_1))
    thread6 = threading.Thread(target=scrapAnilist, args=(anime_data_thread6,top_AniList_url))




    #wait thread 4 to finish to start 1 & 2
    thread4.start()
    thread4.join()
    # Start 1 & 2 & 5 threads
    thread1.start()
    thread2.start()
    thread5.start()
    thread6.start()



#****
    # Wait for  threads to complete
    thread1.join()
    thread2.join()
    thread5.join()
    thread6.join()


    # Combine my anuime list data
    combined_mal_data = anime_data_thread1 + anime_data_thread2  + anime_data_thread4

    # Save the combined anime details to CSV
    save_anime_details_to_csv(combined_mal_data,anime_data_thread5,anime_data_thread6 ,  'anime_details.csv')

    logging.info(" threads have completed and data is saved to CSV.")

if __name__ == "__main__":
    main()
