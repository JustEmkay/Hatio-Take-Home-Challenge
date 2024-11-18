import requests
from cred import API_URL


def header( token: dict ) -> dict:
    
    return {"Authorization": f"{token['token_type']} {token['access_token']}"}
    
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
  
def register_user(register) -> dict:
    """ API call to **User Registration** """
    
    req = requests.post(API_URL + 'register',json=dict(register))
    res = req.status_code
    if res == 200:
        return req.json()

def userProfile(token: str) -> dict:
    
    req = requests.post(API_URL + "users/profile",headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()

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
    
def updateTodoDesc( pid: str, tid: str, desc: bool, token: str ) -> dict:
    
    url = f"projects/todos/edit/{pid}/{tid}?option=update&sdesc={desc}"
    
    req = requests.put(API_URL + url,
                       headers=header(token))
    res = req.status_code
    if res == 200:
        return req.json()
    
  
# def test(token: dict) -> dict:
#     req = requests.post(API_URL + "test",headers=header(token))
#     res = req.status_code
#     if res == 200:
#         print(req.json())