from fastapi import FastAPI, HTTPException, Depends, Header
import jwt, jwt.exceptions
import uuid, bcrypt, time
from typing import Annotated,List
from pydantic import BaseModel
from manager import *
from datetime import datetime, timezone, timedelta


now_Timestamp : int = int(datetime.now().timestamp())
exp = datetime.now(timezone.utc) + timedelta(hours=6) #token expire time
now = datetime.now(timezone.utc)

# secret keys 
SECRET_KEY = "76bb3730fcdb94e622e6f570a629337a371a1a68"
ALGORITHM = "HS256"


app = FastAPI()

#============================================================
# Pydantic Models - Schema
#============================================================
class LoginInfo(BaseModel):
    username : str
    password : str

class RegisterInfo(BaseModel):
    username : str    
    email : str
    password : str

class ProjectInfo(BaseModel):
    title : str
    todos : List[str]
    pid : str = str(uuid.uuid1())
    created_date : int = now_Timestamp

class TodoInfo(BaseModel):
    pid: str
    description: str
    tid: str= None
    cd: int= now_Timestamp
    ud: int= now_Timestamp
    status: bool= False

class Profile(BaseModel):
    uid : str
    username : str
    email : str

class Todos(BaseModel):
    tid: str
    description: str
    status: int
    created_date: int
    updated_date: int

class Projects(BaseModel):
    pid: str 
    title: str
    created_date: int
    todos: list[Todos]


#============================================================
# dependency-injection
#============================================================

class VerifyUser:
    
    def verify( self, login: LoginInfo ) -> bool:
        
        if checkUser(login.username):
            hpassword : bytes = getPassword(login.username)
            
            if verify_pass(login.password, hpassword):
                return True
            
        return False
    
    #=====================
    def createToken( self, uid: str, username: str ) -> str:
        
        payload_data : dict = {
            'uid': uid,
            'username': username,
            'iat': now,
            'exp': exp
        }
        
        token = jwt.encode(
            payload= payload_data,
            key= SECRET_KEY,
            algorithm= ALGORITHM
        )

        return token
        
    #=====================
    def validateToken( self, token: str ) -> dict:
        
        try:
            valtoken = jwt.decode(token, SECRET_KEY, ALGORITHM)
            return valtoken    
         
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Your token Expired!')
        
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail='Unauthorized-!')
        
    #=====================
    def headerTokenVal( self, headerStr: str) -> dict:
        
        if not headerStr.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Authorization header must start with 'Bearer'")

        token = headerStr.split(" ")[1]
        return self.validateToken(token)
        
            
def get_verified():
    return VerifyUser()

verifyUserService = Annotated[VerifyUser, Depends(get_verified)]
accessHeaderStr = Annotated[str, Header()]



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
async def register_account(register: RegisterInfo) -> dict:
        
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
                  email = register.email,
                  password = hash_pass(register.password)):
        
        
        return {
            'status' : True,
            'msg' : 'Created account successful.'
        }
    
    return {
        'status' : False,
        'msg' : 'Failed tto create account.'
    }

@app.post("/login")
async def login_account(login: LoginInfo ) -> dict:
    
    verifyService = verifyUserService()
    if verifyService.verify(login):
        
        userIDs = getUser(login.username)
        token = verifyService.createToken( userIDs['uid'], userIDs['username'])
        
        return { "status": True, "access_token": token, "token_type": "Bearer"}
    
    return { 'status': False, 'msg': 'Wrong credentials.' }
        
@app.post("/users/profile", response_model= Profile)
async def get_userProfile(Authorization : accessHeaderStr):

    userdata = verifyUserService().headerTokenVal(Authorization)
    result = getUserProfile(userdata['uid'])

    return result

@app.get("/projects", response_model= list[Projects])
async def get_projects(Authorization : accessHeaderStr) -> dict:

    userdata = verifyUserService().headerTokenVal(Authorization)
    if userdata['uid']:    
        projects : list[dict] = getAllProjects(userdata['uid'])
        return projects
    

    return []

@app.post("/projects/create")
async def create_project( project: ProjectInfo, Authorization: accessHeaderStr ) -> dict:
    
    userdata = verifyUserService().headerTokenVal(Authorization)
    
    if insertProject( userdata['uid'], project ):
    
        for todo in project.todos:
            ti = TodoInfo( tid= str(uuid.uuid1()), pid= project.pid, description= todo )
            time.sleep(0.5)
            if insertTodo(ti):
                print("Created Todo")
            else:
                print("Created Todo")
        
        return { 'status': True, 'msg': 'Createtd Project successfully.' }
    return { 'status': False, 'msg': 'Failded to created Project'  }
            
@app.put("/projects/update/{pid}")
async def update_project( pid: str, title: str, Authorization: accessHeaderStr):
    
    userData = verifyUserService().headerTokenVal(Authorization)
    
    if projectDeleteUpdate(option='update', uid=userData['uid'],
                        pid=pid, title=title):
        
        return {
            'status' : True,
            'msg' : 'Updated title.'
        }
        
    return {
        'status' : False,
        'msg' : 'Failed to update title.'
    }
           
@app.delete("/projects/delete/{pid}")
async def delete_project(pid:str , Authorization: accessHeaderStr):
    
    userData = verifyUserService().headerTokenVal(Authorization)
    
    if projectDeleteUpdate(option='delete', uid=userData['uid'],
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
    
@app.post("/projects/todos/create/{pid}")
async def create_todos( pid: str, todo: dict , Authorization: accessHeaderStr):
 
    todoInfo = TodoInfo( pid= pid,
                        description= todo['description'],
                        tid= str(uuid.uuid1()))
    
    userData = verifyUserService().headerTokenVal(Authorization)
    if userData['uid']:
        if insertTodo(todoInfo):
            
            return {
                'status':True,
                'msg' : 'created todo successfully'
            }
            
        return {
                'status':False,
                'msg' : 'failed to create todo'
            }

@app.put("/projects/todos/edit/{pid}/{tid}")
async def update_todos(pid: str, tid: str,
                       Authorization: accessHeaderStr,
                       desc: str = None,
                       status: bool = None):
    
    userdata = verifyUserService().headerTokenVal(Authorization)
    
    if userdata:
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

@app.delete("/projects/todos/delete/{pid}/{tid}")
async def delete_todo( pid: str, tid: str, Authorization: accessHeaderStr):
    
    userdata = verifyUserService().headerTokenVal(Authorization)
    if userdata['uid']:
        if todosDeleteUpdate(pid=pid, tid=tid, option='delete'):
            return {
                'status': True,
                'msg' : 'Deletion successful.'
            }
    return {
                'status': False,
                'msg' : 'Failed to delete todo.'
    }
    


@app.post("/test")
async def test_things(Authorization : accessHeaderStr):
    
    return verifyUserService().headerTokenVal(Authorization)
    