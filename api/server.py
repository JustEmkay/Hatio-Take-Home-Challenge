from fastapi import FastAPI
import uuid,bcrypt
from pydantic import BaseModel
from manager import *
from datetime import datetime

now_Timestamp : int = int(datetime.now().timestamp())

app = FastAPI()

#============================================================
# Pydantic Models - Schema
#============================================================
class LoginInfo(BaseModel):
    userinput : str
    password : str

class RegisterInfo(BaseModel):
    username : str    
    email : str
    password : str

class ProjectInfo(BaseModel):
    uid : str
    title : str
    pid : str = uuid.uuid1()
    created_date : int = now_Timestamp

class TodoInfo(BaseModel):
    pid : str
    description : str
    tid : str = uuid.uuid1()
    cd : int = now_Timestamp
    ud : int = now_Timestamp



#============================================================
# Functions 
#============================================================
def hash_pass(userPass:str) -> str:
    pswd = userPass.encode('utf-8')
    return bcrypt.hashpw(pswd,bcrypt.gensalt())

def verify_pass(userPass:str, hashedPass:str) -> bool:
    pswd = userPass.encode('utf-8')
    return bcrypt.checkpw(pswd,hashedPass)

def verify_uid(uid:str) -> bool:
    verifyUID(uid)



#============================================================
# HTTP methods 
#============================================================
@app.get("/")
async def connection():
    return {
        'status' : True,
        'autor' : 'emkay'
    }
    
@app.post("/register")
async def register_account(register:RegisterInfo):
        
    if checkUser(register.username):
        return {
            'status':False,
            'msg':'Try another username.'
        }
    
    if checkUser(register.email):
        return {
            'status':False,
            'msg':f'You already have an account.\
                try recovering it.'
        }
    
    if insertUser(uid = str(uuid.uuid1()),
                  username = register.username,
                  email = register.username,
                  password = hash_pass(register.password)):
        
        
        return {
            'status' : True,
            'msg' : 'Created account successful.'
        }
    
    return {
        'status' : False,
        'msg' : 'Failed tto create account.'
    }

@app.post("/login/")
async def login_aacount(login:LoginInfo):
    
    if checkUser(login.userinput):
        hpassword : bytes = getPassword(login.userinput)
        if verify_pass(login.password, hpassword):
            
            auth = getUser(login.userinput)
            
            return {
                'status' : True,
                'msg':'Verified.',
                'auth': auth
            }
            
    return {
        'status' : False,
        'msg':'Failed to verify.'
    }
    
@app.get("/projects/{uid}")
async def get_projects(uid:str):
    
    if verifyUID(uid):    
        projects : list[dict] = getAllProjects(uid)
        
        return {
            'status': True,
            'projects' : projects
        }
    return {
        'status' : False,
        'msg' : 'invalid UID.'
    }

@app.post("/projects/create")
async def create_project(project:ProjectInfo):
    
    if verifyUID(project.uid):
        
        insertProject(project)
        
        return {
            'status':True,
            'msg': 'Created new project.'
        }
        
        
    return {
        'status': False,
        'msg': 'Failed to create new project.'
    }
        
@app.put("/projects/update/{uid}/{pid}")
async def update_project(uid:str, pid:str, title:str):
    
    if projectDeleteUpdate(option='update', uid=uid,
                        pid=pid, title=title):
        
        return {
            'status' : True,
            'msg' : 'Updated title.'
        }
        
    return {
        'status' : False,
        'msg' : 'Failed to update title.'
    }  
       
@app.delete("/projects/delete/{uid}/{pid}")
async def delete_project(uid:str, pid:str):
    
    if projectDeleteUpdate(option='delete', uid=uid,
                        pid=pid):
            
        return {
            'status' : True,
            'msg' : 'Deleted whole project.'
        }
    
    return {
        'status' : False,
        'msg' : 'Deletion of Project failed.'
    }
    
@app.get("/todos/{pid}") 
async def get_todos(pid:str):
    
    todos = getAllTodos(pid)
    
    return {
        'todos' : todos
    }
    
@app.post("/todos/create")
async def create_todos(todo : TodoInfo):
    
    if insertTodo(todo):
        
        return {
            'status':True,
            'msg' : 'created todo successfully'
        }
        
    return {
            'status':False,
            'msg' : 'failed to create todo'
        }

@app.put("/todos/update/{pid}/{tid}")
async def update_todos(pid:str, tid:str, desc:str = None, status : int = None):
    
    if todosDeleteUpdate(pid=pid, tid=tid, option='update', desc=desc,
                         status=status, ud=now_Timestamp):
        return {   
            'status' : True,
            'msg' : 'Updated.'
        }
    
    return {
        'status' : False,
        'msg' : 'Failed to update.'
    }