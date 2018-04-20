#Import Flask Library
import hashlib
import datetime
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
#from sqlalchemy.exc import IntregrityError

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       port = 3306,
                       db='plan_it',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
        cursor = conn.cursor();
        today = datetime.date.today()
        
        cursor.close()
        return render_template('index.html')


#Define route for login
@app.route('/login')
def login():
        return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
        return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
        #grabs information from the forms
        username = request.form['username']
        password = request.form['password']

        #cursor used to send queries
        cursor = conn.cursor()

        #executes query
        h = hashlib.md5()
        h.update(password.encode('utf-8'))
        query = 'SELECT * FROM member WHERE username = %s and password = %s'
        cursor.execute(query, (username, h.hexdigest()))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
                #creates a session for the the user
                #session is a built in
                session['username'] = username
                return redirect(url_for('home'))
        else:
                #returns an error message to the html page
                error = 'Invalid login or username'
                return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
        #grabs information from the forms
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        zipcode = request.form['zipcode']

        cursor = conn.cursor()
        query = 'SELECT * FROM member WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        error = None
        if(data):
                #If the previous query returns data, then user exists
                error = "This user already exists"
                return render_template('register.html', error = error)
        else:
                h = hashlib.md5()
                h.update(password.encode('utf-8'))
                ins = 'INSERT INTO member VALUES(%s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (username, h.hexdigest(), firstname, lastname, email, zipcode))
                conn.commit()
                cursor.close()
                return render_template('index.html')

def registerAuth():
        #grabs information from the forms
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        zipcode = request.form['zipcode']

        cursor = conn.cursor()
        query = 'SELECT * FROM member WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        error = None
        if(data):
                #If the previous query returns data, then user exists
                error = "This user already exists"
                return render_template('register.html', error = error)
        else:
                h = hashlib.md5()
                h.update(password.encode('utf-8'))
                ins = 'INSERT INTO member VALUES(%s, %s, %s, %s, %s, %s)'
                cursor.execute(ins, (username, h.hexdigest(), firstname, lastname, email, zipcode))
                conn.commit()
                cursor.close()
                return render_template('index.html')

@app.route('/home')
def home():
        username = session['username']
        cursor = conn.cursor();

        today = datetime.datetime.now()
        #fetches events in the next 3 days
        query = 'SELECT party_id, title, type_of_party, description, start_time, end_time FROM party NATURAL JOIN belongs_to WHERE username = %s'
        cursor.execute(query, username)
        eventData = cursor.fetchall()

        
        cursor.close()
        return render_template('home.html', eventData = eventData)



'''
Create an event : If the user is authorized to do so,
he or she creates a new event for a group, providing
all the needed data, via forms. The application should
prevent unauthorized users from doing this action.
'''

@app.route('/create_event', methods=['GET', 'POST'])
def createEvent():
        username=session['username']
        cursor = conn.cursor();

        title = request.form['title']
        type = request.form['type_of_party']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        now = datetime.datetime.now()
        isFuture = str(now) < start_time
        isAfter = end_time > start_time


        if (isFuture and isAfter):
                query = 'insert into location VALUES ()'
                cursor.execute(query)

                query = 'insert into shopping_cart (location_id) VALUES ((SELECT MAX(location_id) FROM location))'
                cursor.execute(query)

                query = 'insert into party (title, type_of_party, description, start_time, end_time, shopping_cart_id) VALUES (%s, %s, %s, %s, %s, (SELECT MAX(shopping_cart_id) FROM shopping_cart))'
                cursor.execute(query, (title, type, description, start_time, end_time))

                query = 'insert into belongs_to (party_id, username) VALUES ((SELECT MAX(party_id) FROM party), %s)'
                cursor.execute(query, (username))

                conn.commit()
                cursor.close()
                return render_template('choose_item.html')
        else:
                return render_template('error.html')


@app.route('/guest_status', methods=['GET', 'POST'])
def guestStatus():
        username=session['username']
        cursor = conn.cursor();

        party_id = request.form['party_id']

		#check if group  exists
        partyExistsQuery = 'select party_id from belongs_to WHERE username = %s'
        cursor.execute(partyExistsQuery, username)
        partyExistData = cursor.fetchone()
        party_exist = False
        if (partyExistData):
                party_exist = True
  
        if (party_exist):
                query = 'SELECT guest_name, email, status FROM guest_list NATUAL JOIN guest WHERE party_id = %s'
                cursor.execute(query, party_id)
                guestData = cursor.fetchall()
                cursor.close()
                return render_template('guest_status.html')
        else:
                return render_template('error.html')

@app.route('/logout')
def logout():
        session.pop('username')
        return render_template('bye.html')
                
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
        app.run('0.0.0.0', 5000, debug = True)
