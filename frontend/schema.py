from pydantic import BaseModel


class loginInfo(BaseModel):
    username : str
    password : str
    
class registrationInfo(BaseModel):
    username : str
    email : str
    password : str
        
class Project(BaseModel):
    title : str
    todos : list
    
class TodoModel(BaseModel):
    tid: str | None = None
    description: str | None = None
    status: bool = 0