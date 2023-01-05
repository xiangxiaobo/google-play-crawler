import random
import logging
import sqlite3
import time
import sys
from google_play_scraper import search

global conn, cur

def init():
    logging.basicConfig(level=logging.DEBUG)
    init_database()
    # check_device()

def get_list_of_words(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def save_metadata(app_id, installs, developer, genre, title):
    query_str = """select * from appinfo where appid='{}'""".format(app_id)
    cur.execute(query_str)
    result = cur.fetchall()
    if result is None or len(result)==0:
        # insert into database
        logging.info("inser into database: {}".format(app_id))
        insert_cmd = """insert into appinfo values(?,?,?,?,?,?)"""
        cur.execute(insert_cmd, (app_id, installs, developer, genre, title, 0))
        conn.commit()
    else:
        logging.info("found duplicate appid: {}".format(app_id))

def filt_and_save_meta(input_list):
    output_list = []
    for item in input_list:
        if not item['free']:
            continue
        installs = int(item['installs'].replace("+","").replace(",",""))
        if installs < 100000000:
            # filter google play bug bounty targets.
            continue
        save_metadata(item['appId'], installs, item['developer'], item['genre'], item['title'])
        output_list.append(item['appId'])
    return output_list

def init_database():
    global conn, cur
    conn = sqlite3.connect("./app_metadata.db")
    cur = conn.cursor()
    create_table = """create table if not exists appinfo(
        appid archar(255),
        installs integer,
        developer varchar(255), 
        genre varchar(255), 
        title varchar(255),
        downloaded integer
    )
    """
    cur.execute(create_table)
    conn.commit()

def main():
    init()
    words = get_list_of_words("./wordlist.10000.txt")
    while True:
        rand_word = random.choice(words)
        for retry in range(10):
            try:
                search_result = search(rand_word)
                logging.debug("searching rand_word:{}, result:{}".format(
                    rand_word, len(search_result)))
                break
            except:
                logging.error("search error, retrying...")
                time.sleep(2)
        filtered_result = filt_and_save_meta(search_result)

if __name__ == "__main__":
    main()