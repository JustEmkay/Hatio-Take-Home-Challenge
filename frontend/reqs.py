import requests

API_URL = 'http://127.0.0.1:8000/'

class HttpException(Exception):
    def __init__(self, status_code, message=""):
        self.status_code = status_code
        self.message = message or f"HTTP Error {status_code}"
        super().__init__(self.message)

#============================================================
# Functions
#============================================================

def header( token: dict ) -> dict:
    
    return {"Authorization": f"{token['token_type']} {token['access_token']}"}

#============================================================
# Streamlit HTTP requests
#============================================================
    
def get_connection() -> dict:
    
    req = requests.get(API_URL)
    res = req.status_code 
    if res == 200:
        return req.json()    

def verify_user(login) -> dict:
    """ API call to **User Login** """    
    
    req = requests.post(API_URL + "login",json=dict(login))
    res = req.status_code 
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")   
  
def register_user(register) -> dict:
    """ API call to **User Registration** """
    
    req = requests.post(API_URL + 'register',json=dict(register))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")

def userProfile(token: str) -> dict:
    
    req = requests.post(API_URL + "users/profile",headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")

def userProjects(token: str) -> dict:
    
    req = requests.get(API_URL + "projects",headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()

def insertProject( token: str, project ) -> dict:
    
    req = requests.post(API_URL + "projects/create",
                       json=dict(project),
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()

def deleteProject( token: str, pid: str ) -> dict:

    req = requests.delete(API_URL + f"projects/delete/{pid}",
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()

def updateTodoStatus( pid: str, tid: str, status: bool, token: str ) -> dict:
    
    url = f"projects/todos/edit/{pid}/{tid}?option=update&status={status}"
    
    req = requests.put(API_URL + url,
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")
    
def updateTodoStatusDesc( pid: str, tid: str, desc: str, status: bool, token: str ) -> dict:
    
    url = f"projects/todos/edit/{pid}/{tid}?desc={desc}&status={status}"
    req = requests.put(API_URL + url,
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")
    
def updateProject( pid: str, title: str, token: str  ) -> dict:
    
    req = requests.put(API_URL + f"projects/update/{pid}?title={title}",
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")

def insertTodo( pid: str, token: str, todo ) -> dict:
    
    req = requests.post( API_URL + f"projects/todos/create/{pid}",
                        headers=header(token),
                        json=dict(todo))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")    
  
def deleteTodo( pid: str, tid: str, token ) -> dict:
    
    req = requests.delete( API_URL + f"projects/todos/delete/{pid}/{tid}",
                          headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    elif res == 401:
        raise HttpException(401, "Token Expired")

#============================================================
# Github gist Request
#============================================================

def createGithubGist( access_token: str, filename: str,
                     content: str, description: str, isPublic: bool ) -> dict:
    
    url = "https://api.github.com/gists"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }
    
    payload = {
        "description": description,
        "public": isPublic,
        "files": {
            filename: {
                "content": content,
            }
        },
    }

    # Make the POST request to create the Gist
    resp = requests.post(url, json=payload, headers=headers)
    
    if resp.status_code == 201:
        return {
            'status' : True,
            'url' : resp.json().get('html_url'),
            'id' : resp.json().get('id')
        }
    else:
        return {
            'status' : False,
            'msg' : resp.text
        }

