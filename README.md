

***Overview***

```
The script is designed to scrape 10000 anime data from 3 different websites 
1- MyAnimeList (MAL):
2-IMDb :
3- AniList:
 using a combinationof Selenium for dynamic content and BeautifulSoup  for parsing static HTML content.
It leverages multithreading to efficiently scrape multiple pages in parallel and aggregates the data into a CSV file for further analysis.

```


Run Script using : ```./run_main```

You can run the scraping only using : ```python3 scraper.py```

Scraped data is saved in:```anime_details.csv```
 
Plots and reprorts saved to : top100.pdf , top_anime_by_genre.pdf plots.pdf , still_streaming.pdf
