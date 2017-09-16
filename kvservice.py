from flask import request, g
from flask_api import FlaskAPI, status
import sqlite3
import dbm.dumb as dbm

app = FlaskAPI(__name__)

CREATE_QUERY = '''
CREATE TABLE kv (
    key TEXT PRIMARY KEY,
    value TEXT
);
'''

DBFILE = "kv.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DBFILE)
        db.row_factory = sqlite3.Row

        try:
            cur = db.execute("select * from kv where 0")
        except sqlite3.OperationalError:
            db.execute(CREATE_QUERY)

    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/key/", methods=["GET", "PUT"])
def nokey():
    if request.method == "GET":
        cur = get_db().execute("select key,value from kv")
        rv = cur.fetchall()
        cur.close()

        return {item["key"]:item["value"] for item in rv}

    elif request.method == "PUT":
        data = {k:str(v) for k,v in request.data.items()}

        db = get_db()
        db.executemany("insert into kv (key,value) values (?,?)", data.items())
        db.commit()

        return data, status.HTTP_201_CREATED

@app.route("/key/<key>", methods=["GET", "POST", "PUT", "DELETE"])
def haskey(key):
    if not key:
        return "", status.HTTP_400_BAD_REQUEST

    if request.method == "GET":
        cur = get_db().execute("select value from kv where key=?", (key,))
        rv = cur.fetchone()
        cur.close()

        return {"value": rv["value"]}

    elif request.method == "POST":
        value = request.data.get("value")
        if not value:
            return "", status.HTTP_400_BAD_REQUEST

        db = get_db()
        db.execute("update kv set value=? where key=?", (value, key))
        db.commit()

        return dict(key=key, value=str(value)), status.HTTP_202_ACCEPTED

    elif request.method == "PUT":
        value = request.data.get("value")
        if not value:
            return "", status.HTTP_400_BAD_REQUEST

        db = get_db()
        db.execute("insert into kv (key,value) values (?,?)", (key, value))
        db.commit()

        return dict(key=key, value=str(value)), status.HTTP_201_CREATED

    elif request.method == "DELETE":
        db = get_db()
        db.execute("delete from kv where key=?", (key,))
        db.commit()

        return "", status.HTTP_204_NO_CONTENT
