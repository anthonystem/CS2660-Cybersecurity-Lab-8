from authentication import hash_password
import config
import os
import sqlite3

class Database:
    
    CREATE_USERS_TABLE = """
                            CREATE TABLE IF NOT EXISTS Users (
                                user_id integer PRIMARY KEY,
                                username varchar(16) NOT NULL,
                                password varchar(296) NOT NULL,
                                access_level text NOT NULL DEFAULT 'STANDARD'
                            );
                         """
    
    @staticmethod
    def setup(test_mode: bool = False) -> bool:
        connection = sqlite3.connect(config.DATABASE_FILE)
        cursor = connection.cursor()

        # Create Users table.
        cursor.execute(Database.CREATE_USERS_TABLE) 
        
        # Add dummy data to table if in test mode.
        if test_mode:
            test_username = "test"
            test_password = hash_password("Password123!")
            test_access_level = "STANDARD"
            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?);", (test_username, test_password, test_access_level)) 

        connection.commit()
        cursor.close()




