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
#                        password='root',
                       port = 3306,
                       db='plan_it',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
        cursor = conn.cursor();
        today = datetime.date.today()
        
        #fetches events in the next 3 days
        query = 'SELECT event_id, title, start_time, location_name, zipcode FROM party WHERE start_time>= %s AND start_time < DATE(DATE_ADD(%s, INTERVAL 3 DAY))'
        cursor.execute(query, (today, today))
        event_data = cursor.fetchall()

        query = 'SELECT category, keyword FROM interest'
        cursor.execute(query)
        interest_data = cursor.fetchall()
        
        cursor.close()
        return render_template('index.html', event_info = event_data, interest_info = interest_data)

#Define route for find group interest search
@app.route('/group_interest_search', methods=['GET', 'POST'])
def group_interest_search():
        cursor = conn.cursor()
        category = request.form['category']
        keyword = request.form['keyword']
        query = 'SELECT a_group.group_id, group_name, description FROM about NATURAL JOIN a_group WHERE category = %s and keyword = %s'
        cursor.execute(query,(category, keyword))
        group_info = cursor.fetchall()
        cursor.close()
        return render_template('group_info.html', group_info = group_info)

#Defines how to rate an event
@app.route('/rateEvent', methods=['GET', 'POST'])
def rateEvent():
        cursor = conn.cursor()
        username=session['username']
        event_id = request.form['event_id']
        rating = request.form['rating']

        #check if event exists
        eventExistsQuery = 'select event_id from party where event_id = %s'
        cursor.execute(eventExistsQuery, (event_id))
        eventExistData = cursor.fetchone()
        event_exists = False
        if (eventExistData):
                event_exists = True
  
        #get if person was signed up for it
        queryCount = 'select event_id from sign_up where event_id=%s and username = %s'
        cursor.execute(queryCount,(event_id, username))
        eventCount = cursor.fetchone()
        signed_up = False
        if  (eventCount):
                signed_up = True

        #check if event in past
        queryPast = 'select * from an_event where end_time < now() and event_id = %s'
        cursor.execute(queryPast,(event_id))
        eventPast = cursor.fetchone()
        event_past = False
        if  (eventPast):
                event_past = True

        #check if 0-5
        validRating = False
        if (int(rating) >=0 and int(rating) <=5):
                validRating = True
                
        if (signed_up and event_exists and event_past and validRating):
                query = 'update sign_up set rating=%s where username=%s and event_id=%s'
                cursor.execute(query, (rating, username, event_id))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')
        
        
        
        query = 'SELECT a_group.group_id, group_name, description FROM about NATURAL JOIN a_group WHERE category = %s and keyword = %s'
        cursor.execute(query,(category, keyword))
        group_info = cursor.fetchall()
        cursor.close()
        return render_template('group_info.html', group_info = group_info)





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
        query = 'SELECT event_id, title, start_time, location_name, zipcode FROM an_event WHERE start_time>= %s AND start_time < DATE(DATE_ADD(%s, INTERVAL 3 DAY))'
        cursor.execute(query, (today, today))
        eventData = cursor.fetchall()

        query = 'SELECT category, keyword FROM interest'
        cursor.execute(query)
        interest_data = cursor.fetchall()
        

        query = 'SELECT group_name FROM a_group NATURAL JOIN belongs_to WHERE username = %s'
        cursor.execute(query, (username))
        group_data = cursor.fetchall()

        query = 'select event_id, username from sign_up natural join an_event where username in (select friend_to from friend where friend_of = %s) and start_time > now();'
        cursor.execute(query, (username))
        friend_data = cursor.fetchall()

                
        today = datetime.date.today()
        query = 'SELECT event_id, title, start_time, location_name, zipcode FROM an_event NATURAL JOIN sign_up WHERE username = %s AND start_time>= %s AND start_time < DATE(DATE_ADD(%s, INTERVAL 3 DAY))'
        cursor.execute(query, (username, today, today))
        event_data = cursor.fetchall()
        
        query = 'SELECT an_event.event_id, title, an_event.description, start_time, end_time, location_name, an_event.zipcode FROM interested_in NATURAL JOIN about, member, a_group, an_event, organize WHERE interested_in.username = member.username AND a_group.group_id = about.group_id AND a_group.group_id = organize.group_id AND an_event.event_id = organize.event_id AND member.username = %s and start_time > now()'
        cursor.execute(query, (username))
        int_event_data = cursor.fetchall()


        #shows average rating for events in the PAST
        #where events are organized by group that user belogns to
        query = 'select event_id, avg(rating) as average from sign_up where event_id in (select event_id from organize natural join an_event where end_time < now() and group_id in (select group_id from belongs_to where username = %s)) group by event_id'
        cursor.execute(query, (username))
        average_ratings = cursor.fetchall()

        query = 'select username from interested_in where category in (select category from interested_in where username=%s) and (not username = %s)'
        cursor.execute(query, (username, username))
        others_interested = cursor.fetchall()

        #display authorized groups user can make events for
        query = 'select group_id from belongs_to where username = %s and authorized=1' 
        cursor.execute(query, (username))
        authorized = cursor.fetchall()

        #seeing post event details for events in the past
        query = 'select * from post_event_details'
        cursor.execute(query)
        post_event_details = cursor.fetchall()
        cursor.close()
        return render_template('home.html', interest_data = interest_data, eventData = eventData, authorized=authorized, post_event_details = post_event_details, others_interested = others_interested, friend_info = friend_data, username=username, group_info=group_data, event_info = event_data, int_event_info = int_event_data, average_ratings=average_ratings)



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

        event_id = request.form['event_id']
        title = request.form['title']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location_name = request.form['location_name']
        zipcode = request.form['zipcode']
        group_id = request.form['group_id']

        #these are the groups you are authorized for
        query = 'select group_id from belongs_to where group_id = %s and username = %s and authorized=1' 
        cursor.execute(query, (group_id, username))
        is_auth = False
        authorized = cursor.fetchall()
        if (authorized):
                is_auth = True

        query = 'select event_id from an_event where event_id=%s'
        cursor.execute(query, (event_id))
        is_event_id = True
        eventDuplicate = cursor.fetchall()
        if (eventDuplicate):
                is_event_id = False

        query = 'select location_name from location where location_name=%s and zipcode = %s'
        cursor.execute(query, (location_name, zipcode))
        is_location = False
        locationExists = cursor.fetchall()
        if (locationExists):
                is_location = True

        now = datetime.datetime.now()
        isFuture = str(now) < start_time
        isAfter = end_time > start_time


        if (is_auth and is_event_id and is_location and isFuture and isAfter):
                query = 'insert into an_event VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (event_id, title, description, start_time, end_time, location_name, zipcode))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')


@app.route('/create_location', methods=['GET', 'POST'])
def create_location():
        username=session['username']
        cursor = conn.cursor();

        location_name = request.form['location_name']
        zipcode = request.form['zipcode']
        address = request.form['address']
        location_description = request.form['location_description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        #check if zipcode is 5 digits
        zipcodeValid = len(zipcode) == 5

        #check if latitude and longitude are valid ()
        if (int(latitude) >= 0 and int(latitude) <=90):
                latValid = True
        else:
                latValid = False

        if (int(longitude) >= 0 and int(longitude) <=180):
                lonValid = True
        else:
                longValid = False

        #check if location already exists based on the primary key of table
        query = 'select location_name from location where location_name= %s and zipcode = %s'
        cursor.execute(query, (location_name, zipcode))
        locationExist = cursor.fetchone()
        location_not_exist = True
        if (locationExist):
                location_not_exist = False
                
        if (zipcodeValid and latValid and lonValid and location_not_exist):
                query = 'insert into location VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(query, (location_name, zipcode, address, location_description, latitude, longitude))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')



@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
        username = session['username']
        cursor = conn.cursor();
        group_id = request.form['group_id']

        #check if group  exists
        groupExistsQuery = 'select group_id from a_group where group_id = %s'
        cursor.execute(groupExistsQuery, (group_id))
        groupExistData = cursor.fetchone()
        group_exist = False
        if (groupExistData):
                group_exist = True
  
        #if not already in group
        queryCount = 'select group_id from belongs_to where username = %s and group_id=%s'
        cursor.execute(queryCount,(username, group_id))
        groupAlready = cursor.fetchone()
        group_already = True
        if  (groupAlready):
                group_already = False
        if (group_already and group_exist):
                query = 'INSERT INTO belongs_to VALUES (%s, %s, 0)'
                cursor.execute(query, (group_id, username))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')
        

@app.route('/make_friend', methods=['GET', 'POST'])
def make_friend():
        username = session['username']
        cursor = conn.cursor();
        friend_name = request.form['friend_name']

        #check if friend person exists
        personExistsQuery = 'select username from member where username = %s'
        cursor.execute(personExistsQuery, (friend_name))
        personExistData = cursor.fetchone()
        person_exists = False
        if (personExistData):
                person_exists = True
  
        #if not already friend
        queryCount = 'select friend_to from friend where friend_of = %s and friend_to=%s'
        cursor.execute(queryCount,(username, friend_name))
        friendAlready = cursor.fetchone()
        friend_already = True
        if  (friendAlready):
                friend_already = False
        if (friend_already and person_exists):
                query = 'INSERT INTO friend VALUES (%s, %s)'
                cursor.execute(query, (username, friend_name))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')

        
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
        username = session['username']
        cursor = conn.cursor();
        event_id = request.form['event_id']

        #check if event exists
        eventExistsQuery = 'select event_id from an_event where event_id = %s'
        cursor.execute(eventExistsQuery, (event_id))
        eventExistData = cursor.fetchone()
        event_exists = False
        if (eventExistData):
                event_exists = True
  
        #get if person was signed up for it
        queryCount = 'select event_id from sign_up where event_id=%s and username = %s'
        cursor.execute(queryCount,(event_id, username))
        eventCount = cursor.fetchone()
        signed_up = True
        if  (eventCount):
                signed_up = False
                signed_up_message = 'You are signed up'

        if (signed_up and event_exists):
                query = 'INSERT INTO sign_up (event_id, username, rating) VALUES(%s, %s,0)'
                cursor.execute(query, (event_id, username))
                conn.commit()
                cursor.close()
                return render_template('success.html')
        else:
                return render_template('error.html')

        

@app.route('/remove_sign_up', methods=['GET', 'POST'])
def remove_sign_up():
        username = session['username']
        cursor = conn.cursor();
        event_id = request.form['event_id']

        #check if event exists
        eventExistsQuery = 'select event_id from an_event where event_id = %s'
        cursor.execute(eventExistsQuery, (event_id))
        eventExistData = cursor.fetchone()
        event_exists = False
        if (eventExistData):
                event_exists = True
        
        #get if person was even signed up for it
        queryCount = 'select event_id from sign_up where event_id=%s and username = %s'
        cursor.execute(queryCount,(event_id, username))
        signedCount = cursor.fetchone()
        signed_up = False
        if  (signedCount):
                signed_up = True
        

        #if event is in the future otherwise they should not be allowed to cancel sign up
        queryFuture = 'select event_id from sign_up natural join an_event where event_id =%s and start_time > now()'
        cursor.execute(queryFuture, (event_id))
        eventFuture = cursor.fetchone()
        future = False
        if (eventFuture):
                future = True
        
        if (signed_up and event_exists and eventFuture):
                query = 'delete from sign_up where event_id = %s and username = %s'
                cursor.execute(query, (event_id, username))
                conn.commit()
                cursor.close()
                return render_template('success.html')
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
        app.run('127.0.0.1', 5000, debug = True)
