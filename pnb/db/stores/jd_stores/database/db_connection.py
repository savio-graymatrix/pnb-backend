import mysql.connector
from pnb.db.stores.jd_stores.config.settings import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
