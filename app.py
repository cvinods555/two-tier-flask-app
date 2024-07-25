import os
import time
import MySQLdb
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Use environment variables for database configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', '')

mysql = MySQL(app)

def init_db():
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT
                );
                ''')
                mysql.connection.commit()
                cur.close()
                print("Database initialized successfully")
                break
        except MySQLdb.OperationalError as e:
            print(f"Database connection failed: {e}")
            retries -= 1
            time.sleep(5)
    else:
        print("Failed to connect to the database after several attempts")
        exit(1)

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

