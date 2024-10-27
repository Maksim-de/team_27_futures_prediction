import mariadb
import webzio    
import os
import json
from datetime import datetime
import time
import logging
#from dotenv import load_dotenv


# Define SQLs for inserting data into DB tables
insert_news_sql = """INSERT IGNORE INTO news_data (
                              thread_uuid,
                              post_uuid,
                              site,
                              title,
                              published_timestamp,
                              country,
                              performance_score,
                              domain_rank,
                              language,
                              sentiment,
                              article_text)
                         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
insert_raw_sql = """INSERT IGNORE INTO news_data_raw (
                              thread_uuid,
                              post_uuid,
                              raw_message,
                              published_timestamp)
                         VALUES(?, ?, ?, ?)"""


# Set up Console and File loggers
def handler_exists(logger, handler_class):
    return any(isinstance(handler, handler_class) for handler in logger.handlers)


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('load_news.log')
    #
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)
    #
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)
    #
    if not handler_exists(logger, logging.StreamHandler):
        logger.addHandler(console_handler)
    if not handler_exists(logger, logging.FileHandler):    
        logger.addHandler(file_handler)
    #
    log = logger.info
    loge = logger.error


# Converting a string to timestamp
def to_timestamp(timestamp_str):
    dt = datetime.fromisoformat(timestamp_str)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


# Set up config variables for DB and APP
def set_config():
    #load_dotenv()
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')    
    }
    #
    news_token = os.getenv('NEWS_TOKEN') 
    #
    try: 
        with open('appconfig.json') as f:
            APP_CONFIG = json.load(f)
            APP_CONFIG['news_token'] = news_token
    except FileNotFoundError:
        loge("ERROR: Unable to find appconfig.json")
        raise
    #
    return DB_CONFIG, APP_CONFIG


# Insert dataset into database tables
def execute_db_insert(stmt, dataset, cursor):
    # Attempting to execute bulk insert
    row_cnt = 0
    try:        
        cursor.executemany(stmt, dataset)        
        log(f'Bulk insert processed {cursor.rowcount} rows.')
    except Exception as e:
        loge(f'Batch insert failed for {stmt}; ERROR: {e}')
        # Retrying row by row
        for rec in dataset:
            try:
                cursor.execute(stmt, rec)
                row_cnt += 1
            except Exception as e:
                loge(f"ERROR: unable to execute {stmt}. uuid: {rec[0]}; Exception: {e}")
                r = cursor.fetchall()
        log(f'Single row insert processed {row_cnt} rows.')        


# Prepare list of tuples to be inserted into database tables
def prepare_batch_news(posts, news, news_raw):
    news.clear()
    news_raw.clear()
    for post in posts:
        thread_uuid = post['thread']['uuid']
        post_uuid = post['uuid']
        site = post['thread']['site']
        title = post['thread']['title']
        published_timestamp = to_timestamp(post['published'])
        country = post['thread']['country']
        performance_score = post['thread']['performance_score']
        domain_rank = int(post['thread']['domain_rank'])
        language = post['language']
        sentiment = post['sentiment']
        article_text = post['text']
        raw_post = json.dumps(post)
        # Format the row tuples
        news_row = (thread_uuid, post_uuid, site, title, published_timestamp, country, performance_score, domain_rank, language, sentiment, article_text)
        news_raw_row = (thread_uuid, post_uuid, raw_post, published_timestamp)
        # Add rows to each of the lists
        news.append(news_row)
        news_raw.append(news_raw_row)
    #    
    log(f"Populated news list with {len(news)} records.")    
    
    
def main():   
    setup_logger()
    log("Job started.")
    
    DB_CONFIG, APP_CONFIG = set_config()
    
    try:
        # Attempting to connect to DB
        connection = mariadb.connect(**DB_CONFIG)
        try:
            cursor = connection.cursor()
            # Set up webzio parameters
            token = APP_CONFIG['news_token']  
            query = APP_CONFIG['query']
            webzio.config(token)
            #
            log(f"Loading results of query: {query}")
            #            
            # Execute API call to webzio
            result = webzio.query("filterWebContent", {"q":query})
            more = True
            pageno = 1
            news_data = []
            news_raw = []
            # Start the pagination loop
            while more:
                log(f"Processing page# {pageno}")
                # Prepare rowset for inserting into DB
                prepare_batch_news(result['posts'], news_data, news_raw)
                # Execute DB insert
                execute_db_insert(insert_raw_sql, news_raw, cursor)
                execute_db_insert(insert_news_sql, news_data, cursor)
                # Commit batch
                connection.commit()
                log(f"Committed page {pageno}")
                #
                time.sleep(10)
                # Check if more data to process
                more = int(result['moreResultsAvailable']) > 0
                log(f"More results available: {result['moreResultsAvailable']}")
                log(f"Requests left: {result['requestsLeft']}")
                #
                # Retrieve the next result page from the news provider
                result = webzio.get_next()  
                pageno += 1
        finally:
            # Close the database connection
            connection.close()
    except mariadb.Error as e:
        loge(f"Error connecting to MariaDB: {e}")

    log("Job completed.")

    # Close file handlers
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    main()