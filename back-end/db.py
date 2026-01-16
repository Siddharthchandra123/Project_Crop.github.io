import mysql.connector
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="S1h2a3rd@mnP",
        database="my_database"
    )
def get_all_crops():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT crop_id, crop_name, crop_family, nitrogen_effect
        FROM crops
    """)

    crops = cur.fetchall()

    cur.close()
    db.close()

    return crops
from db import get_db   # if split, else remove

def get_last_crop(land_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT c.crop_id, c.crop_name, c.crop_family, c.nitrogen_effect
        FROM crop_rotation_history r
        JOIN crops c ON r.crop_id = c.crop_id
        WHERE r.land_id = %s
        ORDER BY r.year DESC, r.season_id DESC
        LIMIT 1
    """, (land_id,))

    result = cur.fetchone()

    cur.close()
    db.close()

    return result
def get_land_location(land_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT latitude, longitude
        FROM lands
        WHERE land_id = %s
    """, (land_id,))

    land = cur.fetchone()
    cur.close()
    db.close()
    return land
