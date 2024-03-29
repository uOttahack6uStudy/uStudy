from AzureSQL import AddaUser, DeleteUser, AuthenticateUser, ConnectToAzureSQL,GetCourseID,GetCourseNotifications
from PineconeRAG import SearchInPineconeIndex
from GPTanswers import generate_response
from flask import Flask, render_template,request,flash,session,redirect,url_for
from datetime import datetime  
from flask import jsonify  
from dotenv import load_dotenv
from flask_socketio import SocketIO, join_room, send, emit
import os

MicrosoftEntraPass = os.environ['MICROSOFT_ENTRA_PASSWORD']
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')  
OPENAI_KEY = os.getenv('OPENAI_API_KEY')  


app = Flask(__name__)
app.secret_key = '12334'  
socketio = SocketIO(app)


@app.route('/')    
def index():  
    if 'username' in session:  
        return redirect(url_for('main')) 
    
    else:  
        print("not logged in")
        return redirect(url_for('login'))  # redirect to login route  
    
@app.route('/main', methods=['GET', 'POST'])  
def main():  
    # Initialize 'MiniChatHistory' in the session if it doesn't exist  
    if 'MiniChatHistory' not in session:  
        session['MiniChatHistory'] = []  
    if 'course_clicked' not in session:  
        session['course_clicked'] = ""
  
    if request.method == 'POST':  
        # Check if 'UserQuery' is in request.form  
        if 'UserQuery' in request.form:  
            UserQuery = request.form['UserQuery']  

  
            # Read the contents of the file  
  
            
            answer = generate_response(UserQuery,DocResult,False)
            DocResult = SearchInPineconeIndex(PINECONE_API_KEY,OPENAI_KEY,"ustudy",UserQuery,"syllabus",k=7)
            
            session['MiniChatHistory'].append({'user': UserQuery, 'ai': answer})  
            return jsonify({'ai_response': answer})  
  
        # Check if 'course_code' is in request.form and if 'course_clicked' has changed  
        elif 'course_code' in request.form and session.get('course_clicked') != request.form['course_code']: 
            session['course_clicked'] = request.form['course_code']  
            return redirect(url_for('course'))  
  
    # Check if 'username' is in the session  
    if 'username' in session:  
        return render_template('index.html', username=session['username'].split('@')[0], chat_history=session['MiniChatHistory'])  
    else:  
        return redirect(url_for('login'))  




@app.route('/login', methods=['GET', 'POST'])  
def login():  
    print(f"Request method: {request.method}")  
    print(f"Form data: {request.form}")  
    if request.method == 'POST':  
        username = request.form['username']  
        password = request.form['password']  
        cursor,conn = ConnectToAzureSQL(MicrosoftEntraPass)
        if AuthenticateUser(username, password,cursor,conn):  
            session['username'] = username
            return redirect(url_for('main')) 
        else:
            flash('Invalid credentials. Please try again.', 'error')
        
    return render_template('login.html')  

@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        username = request.form['username']    
        password = request.form['password']    
        print(f"Username: {username}, Password: {password}")    
        cursor,conn = ConnectToAzureSQL(MicrosoftEntraPass)  
        result, message = AddaUser(username, password,cursor,conn)  
        if result:  
            session['username'] = username
            flash('Registration successful!', 'success')  
            return redirect(url_for('main'))   
        else:  
            flash(message, 'error')  
            print(f"error: {message}")
    return render_template('register.html')  

  
@app.route('/AI_Tutor', methods=['GET', 'POST'])  
def AI_Tutor():  
    if 'chat_history' not in session:  
        session['chat_history'] = []  
          
    if request.method == 'POST':  
        UserQuery = request.form['UserQuery']  
        print(session['course_clicked'])  
        DocResult = SearchInPineconeIndex(PINECONE_API_KEY,OPENAI_KEY,"ustudy",UserQuery,session['course_clicked'],k=3)  
        answer = generate_response(UserQuery,DocResult,False)  
        print("details:" + str(DocResult))  
        session['chat_history'].append({'user': UserQuery, 'ai': answer})  
        return jsonify({'ai_response': answer})  
  
    return render_template('AI_Tutor.html', chat_history=session['chat_history'])  




@app.route('/course')
def course():
    if 'username' in session:
        today = datetime.now()  

        print("Today's date:", today)
        
        #today = datetime.strptime(today.strip(), '%Y-%m-%d %H:%M:%S.%f')    

        cursor,conn = ConnectToAzureSQL(MicrosoftEntraPass)
        ID = GetCourseID(session['course_clicked'],cursor,conn)
        Notifications = GetCourseNotifications(ID,cursor,conn)
        DueDate = Notifications[-1]
        DueDate = datetime.strptime(DueDate.strip(), '%Y-%m-%d %H:%M:%S.%f') 
        print(DueDate)         
 
        TimeLeft = DueDate - today
        print(TimeLeft)
        Notifications[-1] = TimeLeft 
        TimeLeft_in_milliseconds = int(TimeLeft.total_seconds() )  
  
        Notifications[-1] = TimeLeft_in_milliseconds   

        print(Notifications[-1])

        return render_template('course.html',username=session['username'].split('@')[0],Notifications=Notifications)
    else:
        return redirect(url_for('login'))
    #return render_template('course.html')

@app.route('/midtermDiscussion')
def midtermDiscussion():
    return render_template('midtermDiscussion.html')

@app.route('/finalDiscussion')
def finalDiscussion():
    return render_template('finalDiscussion.html')

@app.route('/AssignmentHelp')
def assignmentHelp():
    return render_template('assignmentHelp.html')


@socketio.on('message')
def handleMessage(msg):
    username = session.get('username', 'Anonymous')  # Adjust based on how you handle user authentication
    message_data = {'text': msg, 'sender': username}
    emit('message', message_data, broadcast=True)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'sender': 'System', 'text': f'{session.get("username", "Someone")} has joined {room}.'}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)

    