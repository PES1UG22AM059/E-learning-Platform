import mysql.connector
from mysql.connector import Error
from config import Config  # Make sure this is correctly set up and in the right location

def create_connection():
    """Create a database connection to the MySQL database specified by the Config class."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
        connection = None  # Return None if the connection failed
    return connection

def close_connection(connection):
    """Close the database connection."""
    if connection and connection.is_connected():
        connection.close()
        print("The connection to MySQL DB is closed")
