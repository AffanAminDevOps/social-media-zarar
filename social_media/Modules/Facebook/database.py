import psycopg2
from datetime import datetime
import os
import conf

class FacebookDatabase:
    def __init__(self, host, database, user, password):
        self.db_params = {
            "host": host,
            "database": database,
            "user": user,
            "password": password
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_params)
        except psycopg2.Error as e:
            print("Connection error:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_posts_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS posts (
            ID SERIAL PRIMARY KEY,
            Account TEXT,
            Post TEXT,
            Reactions TEXT,
            Shares TEXT,
            Comments TEXT,
            Type TEXT,
            Upload_Time TEXT,
            Shared TEXT,
            Post_Link TEXT,
            Photo BYTEA,              -- Added column for storing images (binary data)
            Updated_At TIMESTAMP      -- Added column for timestamp when updated
        );
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
        except psycopg2.Error as e:
            print("Error:", e)
    

    def insert_into_posts_table(self, data_dict):
        select_sql = """
        SELECT ID, Post_Link, Photo FROM posts WHERE Account = %s AND Post = %s;
        """
        update_sql = """
        UPDATE posts
        SET Reactions = %s, Shares = %s, Comments = %s, Type = %s, Upload_Time = %s, Shared = %s, Post_Link = %s, Photo = %s, Updated_At = %s
        WHERE ID = %s;
        """
        insert_sql = """
        INSERT INTO posts (Account, Post, Reactions, Shares, Comments, Type, Upload_Time, Shared, Post_Link, Photo, Updated_At)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        try:
            cursor = self.connection.cursor()

            # Check if data is already presentdatabase.py
            cursor.execute(select_sql, (data_dict['Account'], data_dict['Post']))
            existing_row = cursor.fetchone()

            if existing_row:
                existing_id, existing_thumbnail, existing_photo = existing_row
                new_thumbnail = data_dict['Post_Link']
                if new_thumbnail == None:
                    new_thumbnail = existing_thumbnail

                if existing_photo is not None:
                    # If photo data is already present, use the existing data
                    photo_data = existing_photo
                else:
                    # If photo data is not present, read and convert the image file to bytes
                    photo_data = None
                    if data_dict['Photo'] != None:
                        with open(data_dict['Photo'], 'rb') as photo_file:
                            photo_data = photo_file.read()
                
                update_values = (
                    data_dict['Reactions'],
                    data_dict['Shares'],
                    data_dict['Comments'],
                    data_dict['Type'],
                    data_dict['Upload Time'],
                    data_dict['Shared'],
                    new_thumbnail,
                    photo_data,           # Use existing or new photo data
                    datetime.now(),
                    existing_id
                )
                cursor.execute(update_sql, update_values)
                self.connection.commit()
            else:
                photo_data= None
                if data_dict['Photo'] != None:
                    # Read and convert the image file to bytes
                    with open(data_dict['Photo'], 'rb') as photo_file:
                        photo_data = photo_file.read()

                values = (
                    data_dict['Account'],
                    data_dict['Post'],
                    data_dict['Reactions'],
                    data_dict['Shares'],
                    data_dict['Comments'],
                    data_dict['Type'],
                    data_dict['Upload Time'],
                    data_dict['Shared'],
                    data_dict['Post_Link'],
                    photo_data,  # Add the Photo data
                    datetime.now()
                )
                cursor.execute(insert_sql, values)
                self.connection.commit()
            if data_dict['Photo'] != None:
                try:
                    os.remove(data_dict['Photo'])  
                except:
                    pass

        except psycopg2.Error as e:
            print("Error:", e)
            print("Error while adding data in database")

def setup_database():
    db_params = {
        "host": conf.host,
        "database": conf.dbname,
        "user": conf.user,
        "password": conf.password
    }
    db = FacebookDatabase(**db_params)
    db.connect()
    db.create_posts_table()
    db.disconnect()
    

def main():
    # Replace with your database connection details
    db_params = {
        "host": "localhost",
        "database": "Facebook",
        "user": "postgres",
        "password": "ticker@1234"
    }

    # Sample test data
    test_data = [
        {
            "Account": "User133",
            "Post": "Post1",
            "Reactions": "1000",
            "Shares": "50",
            "Comments": "3",
            "Type": "Text",
            "Upload Time": "2023-09-08 12:00:00",
            "Shared": "No",
            "Post_Link": None,
            "Photo":None # "photo.jpg"  # File path of the photo
        }
    ]

    try:
        # Initialize the database and create the table
        db = FacebookDatabase(**db_params)
        db.connect()
        db.create_posts_table()

        # Insert test data into the database
        for data_dict in test_data:
            db.insert_into_posts_table(data_dict)

    except Exception as e:
        print("Error:", e)
    finally:
        db.disconnect()

if __name__ == '__main__':
    main()
