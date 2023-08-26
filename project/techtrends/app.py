import sqlite3
from datetime import datetime
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
logging.basicConfig(level=logging.DEBUG)
db_connection_count = 0

# set logger to handle STDOUT and STDERR 
stdout_handler = logging.StreamHandler(sys.stdout)  # stdout handler
stderr_handler = logging.StreamHandler(sys.stderr)  # stderr handler
handlers = [stderr_handler, stdout_handler]
logging.basicConfig(level=logging.DEBUG, handlers=handlers)


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}, Article ID: {post_id} not found!')
      return render_template('404.html'), 404
    else:
      app.logger.info(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}, Article "{post["title"]}" retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}, About Us page retrieved!')
    return render_template('about.html')

# Define the health check
@app.route('/healthz')
def health():
    return jsonify(result="OK - healthy"), 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    global db_connection_count
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(*) FROM posts').fetchone()[0]
    connection.close()
    return jsonify(db_connection_count=db_connection_count, post_count=post_count), 200

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}, Article "{title}" created!')
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
