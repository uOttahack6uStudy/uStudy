from AzureSQL import AddaUser, DeleteUser, AuthenticateUser, ConnectToAzureSQL
from flask import Flask, render_template,request,flash,session,redirect,url_for
from dotenv import load_dotenv
import os

MicrosoftEntraPass = os.environ['MICROSOFT_ENTRA_PASSWORD']

app = Flask(__name__)
app.secret_key = '12334'  


@app.route('/')    
def index():  
    if 'username' in session:  
        return redirect(url_for('main')) 
    
    else:  
        print("not logged in")
        return redirect(url_for('login'))  # redirect to login route  


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


@app.route('/course')
def course():
    return render_template('course.html')

@app.route('/midtermDiscussion')
def midtermDiscussion():
    return render_template('midtermDiscussion.html')

@app.route('/finalDiscussion')
def finalDiscussion():
    return render_template('finalDiscussion.html')

@app.route('/AssignmentHelp')
def assignmentHelp():
    return render_template('assignmentHelp.html')
@app.route('/main')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)