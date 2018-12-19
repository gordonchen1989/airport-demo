import pymysql
import os

class DB:
    """ Database layer
    """

    def query(self, statement):
        #rds settings
        rds_host  = os.environ['DATABASE_HOST']
        db_user = os.environ['DATABASE_USER']
        password = os.environ['DATABASE_PASSWORD']
        db_name = os.environ['DATABASE_DB_NAME']
        port = 3306

        server_address = (rds_host, port)
        conn = pymysql.connect(rds_host, user=db_user, passwd=password, db=db_name, connect_timeout=5, charset='utf8mb4')

        result = None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(statement)
                result = cursor.fetchall()
        finally:
            conn.close()
        return result