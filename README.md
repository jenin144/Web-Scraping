Run Script using : ```python3 scraper.py```

Scraped data is saved in:```MAL_anime_details.csv```

***Overview***

```
The script is designed to scrape anime data from MyAnimeList (MAL) and IMDb using a combinationof Selenium for 
dynamic content and BeautifulSoup  for parsing static HTML content. It leverages multithreading to efficiently scrape 
multiple pages in parallel and aggregates the data into a CSV file for further analysis.

```

 to generate insightful visualizations from the cleaned and aggregated anime data use  ```generate_reports.py```
 
All plots are saved into ```anime_report.pdf``` file using Matplotlib's PdfPages to ensure they are compiled neatly into a single report.
