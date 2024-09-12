from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Set up logging
logging.basicConfig(filename='extracted_titles.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set up Selenium WebDriver
options = Options()
# options.add_argument("--headless")  # Uncomment to run in headless mode
driver = webdriver.Firefox(options=options)

# Define the URL
url = "https://www.imdb.com/search/title/?keywords=anime"
driver.get(url)

# Initialize the list to store titles
imdb_list = []

# Function to extract titles from the current page
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
max_pages = 5  # Set the limit to the number of pages you want to fetch

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

# Print all extracted titles stored in imdb_list
print("\nExtracted Titles:")
for title in imdb_list:
    print(title)
