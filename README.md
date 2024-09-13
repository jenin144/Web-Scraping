

***Overview***

```
The script is designed to scrape 10000 anime data from 3 different websites 1- MyAnimeList (MAL) ,2-IMDb , 3- AniList using a combinationof Selenium for dynamic content and BeautifulSoup  for parsing static HTML content.
It leverages multithreading to efficiently scrape multiple pages in parallel and aggregates the data into a CSV file for further analysis.

```


Run Script using : ```python3 scraper.py```

Scraped data is saved in:```anime_details.csv```

 to generate insightful visualizations from the cleaned and aggregated anime data use  ```generate_reports.py```
 
All plots are saved into ```anime_report.pdf``` file using Matplotlib's PdfPages to ensure they are compiled neatly into a single report.
