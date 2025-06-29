from flask import Flask
import os
from dotenv import load_dotenv
import asyncio
from routes.User.routes import userRoutes
from routes.Files.routes import fileRoutes
from DB import db_connection
from flask_cors import CORS


load_dotenv()
app = Flask(__name__)
CORS(app=app)

app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
try:
    db = db_connection()

except Exception as e:
    exceptionString = f"""
    File Sharing App
    Error: {str(e.message)}
    """


@app.route("/")
def hello():
    if db is not None:
        return f"""
            <h1>File Sharing App</h1>
            <p>Database connected successfully!</p>
            <p>Available collections: </p>
            """
    else:
        return f"""
                <h1>File Sharing App</h1>
                <p>Error: Could not connect to database</p>
                <p> {exceptionString}</p>
                """


app.register_blueprint(userRoutes, url_prefix="/api/users")
app.register_blueprint(fileRoutes, url_prefix="/api/file")

"""
    # Routes
     - /Sign-up -> POST to server which checks database [userid, email, password]
     - /verify/<token> -> GET send a test mail to user to verify the identity
     - /Login -> POST to server and check database if user present or not [email, password]
     
     
     - /upload -> POST to server and upload the file in the database [fileName, fileID]
     - /download/:file_id -> GET to server and search for the file in database using file_id and dowload the file 
      
     - /uploads -> GET to server and return all the files available in the database. 

"""


app.run(debug=True)
