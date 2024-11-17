from pydantic import BaseModel


class loginInfo(BaseModel):
    username : str
    password : str
    
class registrationInfo(BaseModel):
    username : str
    email : str
    password : str
    
# class Todo(BaseModel):
#     description: str
    
class Project(BaseModel):
    title : str
    todos : list