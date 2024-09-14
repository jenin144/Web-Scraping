# Data Pipeline for Web Scraping, Data Cleaning, and Visualization



Run Script using : ```./run_main```

You can run the scraping only using : ```python3 scraper.py```

Scraped data is saved in:```anime_details.csv```
 
Plots and reprorts saved to : ```top100.pdf``` , ```top_anime_by_genre.pdf```  , ```plots.pdf``` , ```still_streaming.pdf```



# ***Overview***

```
The script is designed to scrape 10000 anime data from 3 different websites:
```

```1- MyAnimeList (MAL):``` https://myanimelist.net/topanime.php

```2-IMDb :``` https://www.imdb.com/search/title/?keywords=anime

```3- AniList:``` https://anilist.co/search/anime/top-100?fbclid=IwY2xjawFRFxJleHRuA2FlbQIxMAABHWgq5I0pDoFJzDLBpaQNpx9NMS0Yqp1xUfHruU8WsMYAgL0X_cBWFGNnXQ_aem_xw299XsavXYX8I7Kki8UrA'

 ```
using a combinationof Selenium for dynamic content and BeautifulSoup  for parsing static HTML content.
It leverages multithreading to efficiently scrape multiple pages in parallel and aggregates the data into
 a CSV file for visualize the data and create reports.

```

***Main Tasks:***
```
   - Web Scraping: Extract raw data from multiple websites.

   - Data Cleaning & Transformation: Handle missing data, format inconsistencies, and normalization.

   - Data Storage: csv file is used.

   - Use Python’s schedule library to automate the scraping process.

   - Data Visualization: Create dashboards or reports to visualize trends or key metrics.
```

***Libraries used***
``` 
1-Selenium 
2-BeautifulSoup 
3-Pandas 
4-Requests
5-Matplotlib 

````
