from filmlog import app
from sqlalchemy.sql import text
from flask_login import current_user

# Functions
def result_to_dict(result):
    return [dict(row) for row in result]

# This allows for SQL injection if yuo're not careful!
def next_id(connection, field, table):
    qry = text("""SELECT MAX(""" + field + """) AS currentID FROM """ + table + """ WHERE userID = :userID""")
    result = connection.execute(qry,
        userID = int(current_user.get_id())).fetchone()
    if result.currentID is not None:
        return int(result.currentID) + 1
    else:
        return 1
