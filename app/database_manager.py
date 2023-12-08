from authentication import hash_password
import config
import os
import sqlite3

class DatabaseManager:
    """A class used for making 'admin' level queries and operations for
    testing/convenience purposes.
    """
    CREATE_USERS_TABLE = """
                            CREATE TABLE IF NOT EXISTS Users (
                                user_id integer PRIMARY KEY,
                                username text NOT NULL,
                                password text NOT NULL,
                                access_level text NOT NULL DEFAULT 'STANDARD',
                                blocked integer NOT NULL DEFAULT 0
                            );
                         """
    
    @staticmethod
    def setup(test_mode: bool = False):
        """Creates database file.

        Args:
            test_mode (bool, optional): Adds testing users to database if True.
        """
        try:
            connection = sqlite3.connect(config.DATABASE_FILE)
            cursor = connection.cursor()

            # Create Users table.
            cursor.execute(DatabaseManager.CREATE_USERS_TABLE)    
        except sqlite3.OperationalError:
            print("### ERROR ### Unable to access the database.")
            connection.commit()
            cursor.close()
            return
        
        # Add dummy data to table if in test mode.
        if test_mode:
            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?);", ("test_standard", hash_password("Password123!"), "STANDARD")) 
            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?);", ("test_dm", hash_password("Ilikepie1%"), "DEPARTMENT_MANAGER")) 
            cursor.execute("INSERT INTO Users (username, password, access_level) VALUES (?, ?, ?);", ("test_admin", hash_password("I'mADM1N!#"), "ADMIN")) 

        connection.commit()
        cursor.close()

    @staticmethod
    def nuke():
        """Deletes the database file from the config.
        """
        try:
            os.remove(config.DATABASE_FILE)
        except OSError:
            print(f"### ERROR ### Could not find '{config.DATABASE_FILE}' when attempting delete.")


dbm = DatabaseManager()
dbm.nuke()
dbm.setup(test_mode=True)