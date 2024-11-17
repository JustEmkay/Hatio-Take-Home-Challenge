import sqlite3, uuid
from datetime import datetime
from pathlib import Path
from pprint import pprint

PATH = "database/hatio_todo.db"
tables : tuple[str] = ("users", "projects", "todos")

conn = sqlite3.connect(PATH, check_same_thread=False)
conn.isolation_level = None
cursor = conn.cursor()

def createTables() -> bool:
    
    #============================================================
    #USERS TABLE
    #============================================================
    try:
        cursor.execute( ''' CREATE TABLE IF NOT EXISTS users(
            uid TEXT    PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT  NOT NULL,
            password BLOB   NOT NULL
            ) ''' )
        
    except Exception as e:
        print("Error[users]:",e)
        
    
    #============================================================
    #PROJECTS TABLE        
    #============================================================
    try:
        cursor.execute( ''' CREATE TABLE IF NOT EXISTS projects(
            pid TEXT    PRIMARY KEY,
            uid TEXT    NOT NULL,
            title TEXT NOT NULL,
            created_date INTERGER  NOT NULL,
            FOREIGN KEY (uid)
                REFERENCES users (uid) 
            
            ) ''' )
        
    except Exception as e:
        print("Error[projects]:",e)
        
    
    #============================================================
    #USERS TODOS
    #============================================================       
    try:
        cursor.execute( ''' CREATE TABLE IF NOT EXISTS todos(
            tid TEXT    PRIMARY KEY,
            pid TEXT    NOT NULL,
            description TEXT NOT NULL,
            status INTEGER  DEFAULT 0,
            created_date INTERGER  NOT NULL,
            updated_date INTERGER  NOT NULL,
            FOREIGN KEY (pid)
                REFERENCES projects (pid) 
            ) ''' )
        
    except Exception as e:
        print("Error[todos]:",e)
  
def check_tables() -> bool:
  file = Path(PATH)
  if file.is_file():
      
    #============================================================
    #RETURN ALL TABLES IN DB 
    #============================================================
    cursor.execute( " SELECT name FROM sqlite_master WHERE type='table' " )
    result = [ _[0] for _ in cursor.fetchall() ]
    
    not_in_table : tuple[str] = [ _ for _ in tables if _ not in result ]
    if not not_in_table:
      return "DB found."  
  
  print("DB not found,creating new db")
  ct = createTables()
  if ct['status']:
    return "Task completed."    

def insertUser(**registerInfo) -> bool:
    
    print("userdata:", registerInfo)
    
    try:
        #============================================================
        #ADD USER
        #============================================================ 
        cursor.execute( ''' INSERT INTO users(uid, username, email,
                       password) VALUES(?,?,?,?)''',(registerInfo['uid'],
                       registerInfo['username'], registerInfo['email'],
                       registerInfo['password'],) )
        
        return True
          
    except Exception as e:
          print("Error:",e)

def verifyUID(uid:str) -> bool:
    
    cursor.execute( ''' SELECT 1 FROM users WHERE uid = ? ''', (uid,) )
    result = cursor.fetchone()
    
    if not result:
        return False
    return True
    
def checkUser(userInput:str) -> bool:

    try:
        #============================================================
        #verify if user Exists
        #============================================================
        cursor.execute( f''' SELECT 1 FROM users WHERE username = ?
                       OR email = ? ''', (userInput,userInput,) )
        
        result = cursor.fetchone()

        if result:
            return True
        return False

        
    except Exception as e:
        print('Error at checkUser:',e)    
    
def getPassword(userInput:str) -> bytes:
    
    try:
        #============================================================
        #RETURN hashed password
        #============================================================
        cursor.execute( ''' SELECT password FROM users WHERE username = ? OR email =? ''',
                       (userInput,userInput,))
        
        password = cursor.fetchone()[0]
        return password
        
    except Exception as e:
        print("Error at getPassword: ",e)
        return None

def getUser(userInput:str) -> dict:
    
    #============================================================
    #RETURN uid,username 
    #============================================================
    cursor.execute( ''' SELECT uid,username FROM users WHERE username = ? OR email = ? ''',
                   (userInput,userInput,) )  
    result = cursor.fetchone()
    return {
        'uid' : result[0],
        'username' : result[1]
    }

def getUserProfile(uid: str) -> dict:
    
    #============================================================
    #RETURN uid, username, email 
    #============================================================
    cursor.execute( ''' SELECT username, email FROM users WHERE uid = ? ''',
                   (uid,) )
    result = cursor.fetchone()
    return {
        'uid': uid,
        'username': result[0],
        'email': result[1]
    }
    
def getAllProjects(uid:str) -> list[dict]:
    print("DB-uid:", uid)
    try:
        #============================================================
        #RETURN pid, title, created_date of PROJECTS
        #============================================================
        cursor.execute(''' SELECT pid,title,created_date from projects WHERE uid=? ''', (uid,))
        user_projects = cursor.fetchall()
                
        if not user_projects:
            return []
                
        projects : list[dict] = [ {
            'pid':i[0],
            'title':i[1],
            'created_date':i[2],
            'todos': getAllTodos(i[0]) } for i in user_projects ]
        
        return projects
        
    except Exception as e:
        print("\nError at getAllProjects: ",e)
        return []
          
def insertProject(uid, projectInfo) -> bool:
    
    try:
        #============================================================
        #CREATE NEW PROJECT
        #============================================================
        cursor.execute( ''' INSERT INTO projects(pid, uid, title, created_date) 
                       VALUES(?,?,?,?)''',
                       (projectInfo.pid, uid, projectInfo.title,
                        projectInfo.created_date))
        
        return True
        
        
    except Exception as e:
        print("Error at insertProject: ",e)
        return False
          
def projectDeleteUpdate(**option) -> bool:
    
    if option['option'] == 'update':
        
        try:
            #============================================================
            #UPDATE PROJECT TITLE
            #============================================================
            cursor.execute( ''' UPDATE projects SET title = ? WHERE
                           uid = ? AND pid = ? ''',
                           (option['title'], option['uid'], option['pid'],  ) )
            
            return True
            
        except Exception as e:
            print("Error projectDeleteUpdate[update]:\n",e)
        
        
    if option['option'] == 'delete':
        
        try:
            #============================================================
            #DELETE SPECIFIC PROJECT AND RELATED TODOs
            #============================================================
            cursor.execute( ''' DELETE FROM projects WHERE uid = ? AND pid = ? ''',
                           (option['uid'], option['pid'], ))
                    
            cursor.execute( ''' SELECT 1 FROM todos WHERE pid = ? ''', 
                           (option['pid'],))
            
            result = cursor.fetchone()
            if result:
                
                cursor.execute( ''' DELETE FROM todos WHERE pid = ? ''',
                               (option['pid'],))
                          
            return True
            
        except Exception as e:
            print("Error projectDeleteUpdate[update]:\n",e)

def getAllTodos(pid:str) -> list[dict]:
    
    try:
        #============================================================
        #RETURNS tid, description, status, create_date, update_date
        #============================================================
        cursor.execute( ''' SELECT tid,description, status, created_date,
                       updated_date FROM todos WHERE pid = ?''', (pid,) )
    
        todos_list : list[tuple] = cursor.fetchall()
        if todos_list:
            
            todos : list[dict] = [
                {
                    'tid' : i[0],
                    'description' : i[1],
                    'status' : i[2],
                    'created_date' : i[3],
                    'updated_date' : i[4] 
                    } 
                for i in todos_list]
            
            return todos
        return []
    
    except Exception as e:
        print("Error at getAllTodos:",e)
       
def insertTodo(todoInfo) -> bool:
    
    try:
        #============================================================
        #CREATE NEW TODO
        #============================================================
        cursor.execute( ''' INSERT INTO todos(tid, pid, description,
                       created_date, updated_date) VALUES(?,?,?,?,?)''', (todoInfo.tid,
                        todoInfo.pid, todoInfo.description,
                        todoInfo.cd, todoInfo.ud,) )
        
        return True
        
    except Exception as e:
        print("Error at insertTodo:",e)
        return False
    
def todosDeleteUpdate(**options) -> bool:
    
    if options['option'] == 'update':
        
        update : str = ''
        value : None = None
        
        if options['desc']:
            update : str = f'description = ?'
            value = options['desc']
            
        if options['status']:
            update : str = f"status = ?, updated_date = {options['ud']} "
            value = options['status']
            
        try:
            #============================================================
            #UPDATE status AND description 
            #============================================================
            cursor.execute( f''' UPDATE todos SET {update} WHERE pid = ? AND tid = ? ''',
                           (value, options['pid'], options['tid'],))
            return True
            
        except Exception as e:
            print(" Error at todosDeleteUpdate[update]: ",e)
            return False            
        
    elif options['option'] == 'delete':
        
        try:
            #============================================================
            #DELETE SELECTED todo
            cursor.execute( f''' DELETE FROM todos WHERE pid = ? and tid = ? ''',
                           (options['pid'], options['tid'],))
            return True
            
        except Exception as e:
            print(" Error at todosDeleteUpdate[update]: ",e)
            return False            
        



# def fetch_allProject( uid ):
    
    
#     cursor.execute ( ''' 
                    
#                     SELECT pid, title, created_date
#                     From projects
#                     WHERE uid = ?
                                    
#                     ''', (uid,) )
    
#     projects_data = cursor.fetchall()
    
#     projects : list[dict] = [ { 'pid':i[0],'title':i[1],'created_date':i[2], 'todos': getAllTodos(i[0])  } for i in projects_data ]

#     pprint(projects)


    
# if __name__ == '__main__':
#     pprint(getAllProjects("7919f62d-a1a9-11ef-9f16-d0c5d3da8dc4"))