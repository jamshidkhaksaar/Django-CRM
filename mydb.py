# Install Mysql on your computer
# https://dev.mysql.com/downloads/installer/
# pip install mysql
# pip install mysql-connector
# pip install mysql-connector-python

import mysql.connector

# Your connection details
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'raise_on_warnings': True
}

# Create a connection
connection = mysql.connector.connect(**config)

# Create a cursor
cursor = connection.cursor()

# Execute SQL query to create the database
cursor.execute("CREATE DATABASE elderco")

# Commit the changes
connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()


