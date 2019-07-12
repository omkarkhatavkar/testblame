# db_utils.py
import sqlite3
import os
import requests
import re
from lxml import html
# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path, check_same_thread=False,
                          isolation_level='DEFERRED')
    return con


def set_version(version, failed_test_count, dynamic_graph_count=None,
                search_string=None):
    try:
        db = db_connect()
        cursor = db.cursor()
        if dynamic_graph_count is not None and search_string is not None:
            cursor.execute('''SELECT * FROM dynamic_graph 
                                where version = ? AND search_string = ?''',
                           (version, search_string))
            if cursor.fetchone() is None:
                cursor.execute('''INSERT INTO dynamic_graph
                    (version, search_string, count) VALUES(?, ?, ?)''',
                               (version, search_string, dynamic_graph_count))
            else:
                # update version
                cursor.execute('''Update dynamic_graph set count = ? 
                                    where version = ? AND search_string = ?''',
                               (dynamic_graph_count, version, search_string))

        cursor.execute('''CREATE TABLE IF NOT EXISTS
                          versions(id INTEGER PRIMARY KEY, 
                          version TEXT unique, test_count TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                                  failed_reason(id INTEGER PRIMARY KEY, 
                                  reason TEXT unique, count TEXT)''')
        cursor.execute('''SELECT * FROM versions where version = ?''', (version,))
        is_version_exist = cursor.fetchone()
        if is_version_exist is None:
            # insert version
            cursor.execute('''INSERT INTO versions(version, test_count)
                              VALUES(?, ?)''', (version, failed_test_count))
        else:
            # update version
            cursor.execute('''Update versions set test_count = ? 
                                          where version = ?''', (failed_test_count, version))

        db.commit()
    # Catch the exception
    except sqlite3.IntegrityError as error:
        db.rollback()
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
        raise e
    finally:
        # Close the db connection
        db.close()


def get_test_history():
    try:
        db = db_connect()
        cursor = db.cursor()
        cursor.execute('''SELECT version, test_count FROM versions''')
        all_rows = cursor.fetchall()
        return all_rows
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
    finally:
        # Close the db connection
        db.close()


def get_dynamic_graph_history(pattern):
    try:
        db = db_connect()
        cursor = db.cursor()
        cursor.execute('''SELECT version, count FROM dynamic_graph where 
            search_string = ? ''', (pattern, ))
        all_rows = cursor.fetchall()
        return all_rows
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
    finally:
        # Close the db connection
        db.close()


def set_test_fail_reason(url):
    if bool(url.strip()):
        try:
            db = db_connect()
            page = requests.get(url, verify=False,)
            tree = html.fromstring(page.content)
            failure = tree.xpath('//pre[2]')[0]
            match_1 = re.search('>  .*', failure.text)
            match_2 = re.search('E  .*', failure.text)
            if match_1 and match_2:
                match_1 = match_1.group(0)
                match_2 = match_2.group(0)
            else:
                return None
            fail_reason = match_1 + match_2
            cursor = db.cursor()
            cursor.execute('''SELECT * FROM failed_reason where reason = ?''', (fail_reason,))
            is_version_exist = cursor.fetchone()
            if is_version_exist is None:
                # insert failure reason
                count = 1
                cursor.execute('''INSERT INTO failed_reason(reason, count)
                                          VALUES(?, ?)''', (fail_reason, count))
            else:
                # update count failure reasons
                count = int(is_version_exist[0]) + 1
                cursor.execute('''Update failed_reason set count = ? 
                                                      where reason = ?''', (count, fail_reason))
            db.commit()
        except Exception as e:
            # Roll back any change if something goes wrong
            db.rollback()
            raise e
        finally:
            # Close the db connection
            db.close()
    else:
        return None
