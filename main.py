from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from generate_reports import top_100 as top100
from generate_reports import top_by_genre as topg
from generate_reports import still_straming as stills
from generate_reports import plots as plot
from scraper import main as scrapermain
import logging

# Configure logging
# Configure logging to write logs to a file
logging.basicConfig(
    filename='anime_scraper.log',   # Log file name
    filemode='a',                   # Overwrite the file each time
    level=logging.INFO,             # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'     # Date format for the log
)

logger = logging.getLogger(__name__)

# Create a scheduler instance
scheduler = BackgroundScheduler()

# Define job functions
def run_top100():
    logging.info("Running top100...")
    scrapermain()
    top100()

def run_topg():
    logging.info("Running top_by_genre...")
    scrapermain()
    topg()

def run_stills():
    logging.info("Running still_straming...")
    scrapermain()
    stills()

def run_scrapermain():
    logging.info("Running scraper...")
    scrapermain()
    scrapermain()


def run_plot():
    logging.info("Running plot...")
    scrapermain()
    plot()

scheduler.add_job(run_top100, IntervalTrigger(minutes=43000))  # every month
scheduler.add_job(run_topg, IntervalTrigger(minutes=20160))  # every week
scheduler.add_job(run_stills, IntervalTrigger(minutes=2880))  # every 2 days
scheduler.add_job(run_plot, IntervalTrigger(minutes=20160))   # evey week

# Start the scheduler
scheduler.start()

# Keep the script running
try:
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    # Shut down the scheduler gracefully on exit
    logging.info("Shutting down scheduler...")
    scheduler.shutdown()
