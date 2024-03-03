import pyodbc  
import bcrypt  
import base64
import ast  


from dotenv import load_dotenv  
import os   
  
# Get the API keys from environment variables  


def ConnectToAzureSQL(MicrosoftEntraPass):
    server = 'tcp:docusearchauth.database.windows.net,1433'  
    database = 'DocuSearch'  
    username = 'Hamza.Bouzoubaa@studentambassadors.com'  # my Azure username
    password = MicrosoftEntraPass  # password for the Azure server
    driver= '{ODBC Driver 18 for SQL Server}'  
    
    connection_str = (  
        f"Driver={driver};"  
        f"Server={server};"  
        f"Database={database};"  
        f"Uid={username};"  
        f"Pwd={password};"  
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"  
        f"Authentication=ActiveDirectoryPassword"  
    )  
    
    conn = pyodbc.connect(connection_str)  


    cursor = conn.cursor()  

    return cursor,conn
    
# Select all UstudyUsers  
#cursor.execute("SELECT * FROM UstudyUsers")  
#rows = cursor.fetchall()  
#for row in rows:  
#    print(row)  
  

  
  
def hash_password(password):    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  
    return hashed_password.decode('utf-8')  # decode bytes to string  

  
def check_password(hashed_password, user_password):  
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
      

  
def AddaUser(username, password, cursor, conn):
    if not username or not password:
        print("Error: Username or password cannot be empty")
        return False, "Error: Username or password cannot be empty"
    
    cursor.execute("SELECT COUNT(*) FROM UstudyUsers WHERE Username = ?", (username,))
    result = cursor.fetchone()
    if result[0] > 0:
        print("Username already taken")
        return False , "Username already taken"
    
    hashed_password = hash_password(password)  
    cursor.execute("INSERT INTO UstudyUsers (Username, Password) VALUES (?, ?)", (username, hashed_password))  
    conn.commit()  
    print("User added successfully")  
    return True , "Success: User added successfully"
  
def DeleteUser(username, cursor, conn):  
    cursor.execute("DELETE FROM UstudyUsers WHERE Username = ?", (username,))  
    conn.commit()  
    print("User deleted successfully")  
  
def AuthenticateUser(username, password, cursor, conn):  
    cursor.execute("SELECT Password FROM UstudyUsers WHERE Username = ?", (username,))  
    row = cursor.fetchone()  
    if row is not None:  
        hashed_password = row[0]          
        if check_password(hashed_password.encode("utf-8"), password):  
            print("User authenticated successfully")  
            return True  
    print("User not authenticated")  
    return False 

def AddaFile(filename, UserID, cursor, conn):
    cursor.execute("INSERT INTO Files (Filename, UserID) VALUES (?, ?)", ( filename, UserID))  
    conn.commit()  
    print("File added successfully")  

def DeleteFile(filename, UserID, cursor, conn):
    cursor.execute("DELETE FROM Files WHERE Filename = ? AND UserID = ?", (filename, UserID))  
    conn.commit()  
    print("File deleted successfully") 

def GetFiles(UserID, cursor, conn):
    cursor.execute("SELECT Filename FROM Files WHERE UserID = ?", (UserID,))  
    rows = cursor.fetchall()  
    rows = [row[0] for row in rows]
    return rows

def GetUserID(username, cursor, conn):
    cursor.execute("SELECT ID FROM UstudyUsers WHERE Username = ?", (username,))  
    row = cursor.fetchone()  
    if row is not None:  
        return row[0]
    return None

#AddaFile("test2", 7, cursor, conn)
#print(DeleteFile("test",7, cursor, conn))
#print(GetFiles(10, cursor, conn))
#print(GetUserID("admin", cursor, conn))
#AddaUser("Hamza", "admin00",cursor, conn)
#AuthenticateUser("Hamza", "admin00", cursor, conn)
#print(hash_password("admin00"))

#check_password("ha", password)

