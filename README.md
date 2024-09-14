# Data Pipeline for Web Scraping, Data Cleaning, and Visualization



To run the main script, use : ```./run_main```

To run only the web scraping process, use : ```python3 scraper.py```

You can track the scraping process in the log file: ```anime_scraper.log```

The scraped data is saved in:```anime_details.csv```
 
Plots and reports are saved in:
: ```top100.pdf``` , ```top_anime_by_genre.pdf```  , ```plots.pdf``` , ```still_streaming.pdf```



# ***Overview***

```
The script is designed to scrape 10000 anime data from 3 different websites:
```

```1- MyAnimeList (MAL):  4,600 anime entries ``` https://myanimelist.net/topanime.php

```2-IMDb : 400 anime entries ``` https://www.imdb.com/search/title/?keywords=anime

```3- AniList: 5,000 anime entries ``` https://anilist.co/search/anime/top-100?fbclid=IwY2xjawFRFxJleHRuA2FlbQIxMAABHWgq5I0pDoFJzDLBpaQNpx9NMS0Yqp1xUfHruU8WsMYAgL0X_cBWFGNnXQ_aem_xw299XsavXYX8I7Kki8UrA'

 ```
The script uses a combination of Selenium for dynamic content and BeautifulSoup for parsing static HTML content. It utilizes multithreading to scrape multiple pages simultaneously, then aggregates the data into a CSV file for further visualization and report generation.
```

***Main Tasks:***
```
   - Web Scraping: Extract raw data from multiple websites.

   - Data Cleaning & Transformation: Handle missing data, format inconsistencies, and normalization.

   - Data Storage: The scraped data is saved in a CSV file.

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
6-threading

````


```An example of a plot generated from the scraped data:```

![image](https://github.com/user-attachments/assets/cf7ee460-ddf7-4964-816c-431d128ff833)


