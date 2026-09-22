# REST API for Courses and Course Reviews
Currently runs locally from terminal. API built with Flask on top of Peewee for database management. Created in a Treehouse course.  
The API provides methods to get, post, put, and delete courses and course reviews from a database. The Peewee database also provides a User table which is used as the basis to authenicate access to certain methods with the argon2 package. Courses and their reviews are linked with foreign keys.  
To start, navigate to the parent directory and run in terminal.  
1. Before using it for the first time, be sure to install the required python packages to your virtual environment by running `pip install -r requirements.txt`. Also be create `secret_key.py` in the parent directory. Inside, create a variable called `SECRET_KEY` and assign a random string to it.
2. Run `python3 app.py` or `python app.py`, depending on your operating system.
3. Click the address in terminal.

