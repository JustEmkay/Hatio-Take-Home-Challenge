import streamlit as st 
from datetime import datetime
import re
from schema import *
from reqs import *
import time

#============================================================
# Regex-Validation-Functions | username, email and password
#============================================================

def validate_username(username : str) -> bool:  
    if re.match(r'^(?=[a-zA-Z0-9._]{4,20}$)(?!.*[_.]{2})[^_.].*[^_.]$', username):  
        return True  
    return False

def validate_email(email : str) -> bool:  
    if re.fullmatch(r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", email):  
        return True  
    return False

def validate_password(password : str) -> bool:  
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):  
        return True  
    return False

#============================================================
# Function
#============================================================

def generateOverallSummery( project: dict ) -> dict:
    
    tempPending : list = [ _ for _ in project['todos'] if not _['status'] ]
    tempCompleted : list = [ _ for _ in project['todos'] if _['status'] ]

    markdown_str : str = f"""# {project['title']}\n\n"""
    markdown_str += f" **Summary:** {len(tempPending)}/{len(project['todos'])} todos completed \n\n" 

    markdown_str += f"### Pending ({len(tempPending)}):\n"
    for todo in tempPending:
        markdown_str += f"""- [ ] {todo['description']}\n"""
    if not tempPending:
        markdown_str += " *no pending task.* \n"

    markdown_str += f"### Completed ({len(tempCompleted)}):\n"
    for todo in tempCompleted:
        markdown_str += f"""- [x] {todo['description']}\n"""
    if not tempCompleted:
        markdown_str += " *no task completed* "

    file_name = f"{project['title'].replace(' ', '_').lower()}.md"

    return {
        'markdown' : markdown_str,
        'filename' : file_name
    }

def timeStampToDate( ts: int ) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %I:%M:%S")

@st.cache_data
def returnIndexOfListDict( idname:str , itemid: str, listDict: list[dict]  ) -> int:
    
    tempList : list = [ _[idname] for _ in listDict ] 
    return tempList.index(itemid)

#============================================================
# Logout And clear Session
#============================================================

def logout() -> bool:
    st.session_state.update({})
    st.session_state.update({
  "projects": [],
  "tempProject": {
    "title": None,
    "todos": []
  },
  "auth": {
    "token": {},
    "uid": None,
    "username": None,
    "email": None
  },
  "refreshData": {
    "project": False,
    'tokenExpr' : False
  }
})
    st.rerun()
   
#============================================================
# Streamlit Forms
# * Login 
# * Registration Form [dialog-box]
#============================================================

@st.dialog('Register form')
def registerForm() -> None:
    """ Return **Streamlit registration form[Dialog-Box]**  """
    
    username = st.text_input('Enter your username:')
    email = st.text_input('Enter your email:')
    password = st.text_input('Create your password:',type='password')
    
    alert = st.empty()
    alert.info('Fill all form field.',icon='ℹ')
    
    register = registrationInfo(username=username, email=email,
                                password=password)
        
    if validate_username(register.username) and \
        validate_email(register.email) and \
        validate_password(register.password):
         bttnStatus = False
    else:
        bttnStatus = True
    
    
    if st.button('Create Account',type='primary',disabled=bttnStatus):
        response = register_user(register)
        if response['status']:
            alert.success(response['msg'],icon='✔')
        else:
            alert.warning(response['msg'],icon='⚠')
        
def loginForm() -> None:
    """ Return **Streamlit login form**  """
    
    st.title("Login",anchor=False)
    
    userInput = st.text_input('Username/Email:',value='', placeholder='Enter your username... e.g- manu')
    password = st.text_input("Enter your password:",value='', placeholder='Enter your password.. e.g- 123456789',
                             type='password')
    blnk, su, sn = st.columns([2,1,1])
    
    alert = blnk.empty()
    
    if (validate_username(userInput) or validate_email(userInput)) and validate_password(password):
         bttnStatus = False
    else:
        bttnStatus = True
    
    
    if su.button('sign-up',use_container_width=True):
        registerForm()
    
    if sn.button('sign-in',use_container_width=True,
                 type='primary', disabled=bttnStatus):
        
        login = loginInfo(username=userInput,password=password)
        response = verify_user(login)

        if response['status']:
            st.success("Account login successful.")
            st.session_state.auth['token'] = response
            with st.spinner('Wait for it...'):
                time.sleep(1)
            st.rerun()
            
        else:
            st.warning(response['msg'])
            
#============================================================
# Streamlit Containers dialog-box
#============================================================

@st.dialog("Delete Project!")
def alertDeleteDB( projectID: str, token, projects: dict) -> None:
    
    
    st.caption("⚠ :red[**Confirming this alert will permentally \
        remove this project from database.**]")
    blnk, cnfrm, cncl = st.columns([2,1,1])
    if cnfrm.button("confirm", use_container_width=True): 
        
        delresp = deleteProject( token, projectID )
        if delresp['status']:
            
            st.session_state.projects.pop(
                returnIndexOfListDict( 'pid', projectID, projects))
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failded to delete Project.")
        
    if cncl.button("cancel", use_container_width=True): 
        st.switch_page("home.py")

@st.dialog("logout")
def alertLogout() -> None :
    
    st.caption(":red[Confirming this alert will logout from this account]")
    
    if st.button( 'Confirm',key='logoutalertbttn'):
        
        with st.spinner('loggin out..'):
            time.sleep(0.2)
            if logout():
                st.rerun()
    
 
def downloadButton( filename: str, markdownData: str ) -> None:
    
    st.download_button("Download as .md", file_name= filename,
                    data= markdownData, type='primary',
                    use_container_width= True,
                    help= " Download Gist as **.md** ")
    
@st.dialog("Gist preview 🖼️:" , width='large')
def ProjectGistPreview( project:dict ) -> None:
    mdData= generateOverallSummery( project )   
    
    alert= st.empty()
    export_option : str = st.radio('Select a export option:',
                                    ['Download as .md', "Export as Github gist"],
                                    horizontal= True) 
    if export_option == "Export as Github gist":
        expndr = False
    else: expndr = True
      
    with st.expander('*Project summary*',expanded=expndr):
        st.markdown(mdData['markdown'])
        st.divider()
        
        st.write(f"__Filename:__ *:green[{mdData['filename']}]*")
    
    
    
    if export_option == 'Download as .md':
        downloadButton(mdData['filename'], mdData['markdown'])
        
    if export_option == 'Export as Github gist':
        
        tIn, gistype = st.columns([0.7, 0.3]) 
        
        githubToken = tIn.text_input("Enter Github access token:",
                                    placeholder= "Copy-paste Accesstoken from Github developer settings",
                                    help= " info: [How to generate Github access token](https://www.geeksforgeeks.org/how-to-generate-personal-access-token-in-github/) "
                                    type='password')
        
        Gtype : bool = gistype.selectbox("Gist isPublic",[True, False])
        
        description = st.text_area("Enter Gist description:",
                                   placeholder='Small descripttion about your gist')
        
        if description and githubToken: bttn_status = False
        else: bttn_status = True
        
        if st.button('confirm', key= 'markdownConfirm', use_container_width= True,
                  type= 'primary', disabled= bttn_status):
            resp = createGithubGist( githubToken, mdData['filename'],
                             mdData['markdown'], description, isPublic=Gtype) 

            if resp['status']:
                with alert.container(border=True):
                    st.success("Created Successfully!" , icon= "✅")
                    st.caption("Copy url below to access created Gist")              
                    st.code(f"{resp['url']}")
                    downloadButton(mdData['filename'], mdData['markdown'])
            else:
                with alert.container(border=True):
                    st.error("Something went wrong.")
   
                 
                
# CREATE PROJECT DIALOG-BOX
@st.dialog("Create new project",width='large')
def createProjectDialog(border = True) -> None:
    createProjectContainer(border)

# CREATE PROJECT CONTAINER
def createProjectContainer(border: bool) -> None:
    
    placeholder = st.empty()
    # MAIN CONTAINER    
    with st.container(border=border, height=400):
        
        # DEFINED 2xCOLUMNS
        col1, col2 = st.columns(2) 
        
        # col1 - row1
        with col1.container():
        
            txt, bttn = st.columns([3,1],vertical_alignment='bottom') 
            
            title : str = txt.text_input( "Title of project",
                                        placeholder='Enter project title',
                                        help="Press enter to save changes.")
            st.session_state.tempProject['title'] = title
            if bttn.button('clear',use_container_width=True,
                           help='clear all: title and todos'):
                st.session_state.tempProject = {
                    'title' : None,
                    'todos' : []
                    }
                st.rerun()

            description: str = txt.text_input('Enter todo:',
                                            label_visibility='collapsed',
                                            placeholder="Enter description of todo.")
            if bttn.button('add',use_container_width=True,
                        help='Add todo'):
                st.session_state.tempProject['todos'].append(description)
        
        # col1 - row2
        with col1.container(border=True,height=225):
            if st.session_state.tempProject['todos']:
                st.caption('check checkbox to delete todo.')
                for indx, todo in enumerate(st.session_state.tempProject['todos']):
                    if st.checkbox(todo,key=indx):
                        st.session_state.tempProject['todos'].pop(indx)
                        st.rerun()
            else:
                st.caption("please add todos.")
        
        # col2 - row1                    
        with col2.container(border= True, height=310):
            if st.session_state.tempProject['todos']:
                st.subheader(title,anchor=False,divider=True)
                for indx,todo in enumerate(st.session_state.tempProject['todos'],start=1):
                    st.write( f"{indx}: {todo}" )
            else: 
                st.caption("No preview available")
        
        # col1 - row2       
        if col2.button('Create project',
                    type='primary',
                    use_container_width=True):
            if title and st.session_state.tempProject['todos']:
                
                project = Project(title= title,
                                  todos=st.session_state.tempProject['todos'])
                
                response = insertProject( st.session_state.auth['token'], project )
                
                if response['status']:
                    st.session_state.refreshData['project'] = True
                    placeholder.success(response['msg'],icon='✅')
                    time.sleep(0.5)
                    st.rerun()
                else:
                    placeholder.error(response['msg'],icon='❌')
                    
# TODO-PENDING & COMPLETED LIST
def todoList(pid: str, todos: str)-> None:
    
    tempPending : list = [ _ for _ in todos if not _['status'] ]
    tempCompleted : list = [ _ for _ in todos if _['status'] ]
    
    with st.container(border= True):
        
        if tempPending or tempCompleted:
            
            st.write( f":material/Pending_Actions: **Pending ({len(tempPending)}/{len(todos)}):** " )
            for i in tempPending:
                
                info = fr""" :blue[Created on: **{timeStampToDate(i['created_date'])}** \
                Updated on: **{timeStampToDate(i['updated_date'])}**]"""
                
                if st.checkbox( f"{i['description']}", key= i['tid'], help= info ):
                    res = updateTodoStatus( pid, i['tid'], True, st.session_state.auth['token'] )
                    if res['status']:
                        st.session_state.refreshData['project'] = True
                        st.rerun()
            
            if not tempPending:
                st.write( "*No pending task*" )
            
            
            st.write( f":material/done_all: **Completed ({len(tempCompleted)}/{len(todos)}):** " )
            for i in tempCompleted:
                
                info = fr""" :blue[Created on: **{timeStampToDate(i['created_date'])}** \
                Updated on: **{timeStampToDate(i['updated_date'])}**]"""
                
                if not st.checkbox( f"~{i['description']}~", key= i['tid'], help= info, value=True ):
                    res = updateTodoStatus( pid, i['tid'], False, st.session_state.auth['token'] )
                    if res['status']:
                        st.session_state.refreshData['project'] = True
                        st.rerun()
            
            if not tempCompleted:
                st.write( "*No task Completed*" )
                
        elif not tempPending and not tempCompleted :
            st.write(":grey[*Empty project*]")
             
#PROJECT-LIST
def projectList(projects: dict) -> None:
    
    Caption = f" **Hello :rainbow[{st.session_state.auth['username']}!]** \
    You have created {len(st.session_state.projects)} projects."
    
    cptin, nprjt_bttn, mopt = st.columns([0.7, 0.2, 0.1], 
                                         gap= 'small',
                                         vertical_alignment='bottom')
    
    cptin.info( Caption )
    if nprjt_bttn.button(":material/Create_New_Folder:", use_container_width= True,
                         type='primary', help="Create new project :material/Create_New_Folder:"):
        createProjectDialog()
        
    if mopt.button(":material/logout:",
                use_container_width=True,
                help="Logout :material/logout:"):
        alertLogout()

    
    for idx, project in enumerate( projects ):
        
        subheading = f":grey[Title]: **{project['title']}** ({timeStampToDate(project['created_date'])})"
        
        with st.expander(subheading, expanded= True):
            todoList( project['pid'], project['todos'] )       
    
            blnk, exprt, delt, edit = st.columns([0.25, 0.25, 0.25, 0.25])
            
            if exprt.button('Export', use_container_width=True,
                            help= "Export as ",
                            key=f"{idx}1"):
                ProjectGistPreview( project )
            
            if delt.button('Delete', use_container_width=True,
                           help= ":red-background[❌Delete Project]",
                           key=f"{idx}2"):
                alertDeleteDB(project['pid'], st.session_state.auth['token'], projects)
            
            if edit.button('Edit', use_container_width=True, key=f"{idx}3"):
                editProjectDialogBox( project )
                                       
#EDIT Project
@st.dialog("Edit Project", width='large')
def editProjectDialogBox( project: dict ) -> None:
    
    #UPDATE PROJECT TITLE
    txt_col, bttn_col = st.columns([3,1], vertical_alignment='bottom')
    
    title: str= txt_col.text_input( "Enter new project title", value= project['title'])
    if bttn_col.button('update',key='updateTile', use_container_width=True):
        res = updateProject( project['pid'], title, st.session_state.auth['token'] )
        if res['status']:
            st.success( res['msg'] , icon='✅')    
            st.session_state.refreshData['project'] = True
            time.sleep(0.5)
            st.rerun()
        else:
            st.error(res['msg'], icon='❌')
            
        
        
    #UPDATE/EDIT/DELETE TODOS 
    tempPending : list = [ _ for _ in project['todos'] if not _['status'] ]
    tempCompleted : list = [ _ for _ in project['todos'] if _['status'] ]
    
    placeholder = st.empty()

    TodoEditContainer( placeholder, project['pid'], TodoModel() )
  
    st.caption( ":blue[info:] :blue-background[*select todos using checkbox to **edit**/**delete**/**update**.*]" ) 
    
    with st.container(border=True):
        
        st.write("- **Pending todos:**")
        for todo in tempPending:
            
            if st.checkbox( f"{todo['description']}" ):
                TodoEditContainer(placeholder,  project['pid'], TodoModel(tid= todo['tid'],
                                                         description= todo['description'],
                                                         status= todo['status']))
        
        if not tempPending:
            st.write( "*No pending task*" )
        
        st.divider()
    
        st.write("- **Completed todos:**")
        for todo in tempCompleted:
            
            if st.checkbox( f"~{todo['description']}~" ):
                
                TodoEditContainer(placeholder, project['pid'],  TodoModel(tid= todo['tid'],
                                                         description= todo['description'],
                                                         status= todo['status']))
        
        if not tempCompleted:
            st.write( "*No task Completed*" )
        
# Selected todo edit container
def TodoEditContainer(placeholder, pid: str, todo: TodoModel) -> None:
    
    with placeholder.container(border=True):
        
        delStatus = True

        desc = st.text_input( "Create new todo description:",
        value=todo.description )
            
        stsCol, optCol, addCol = st.columns([0.5, 0.25, 0.25])
        status = stsCol.radio( "Todo status",
                        options= [ False, True ],
                        horizontal=True,
                        index= todo.status,
                        help="True = Completed | False = Pending" )
        
        newTodo = TodoModel(tid= todo.tid,
                            description= desc,
                            status= status)
        

        if not todo.tid: 
            delStatus= True
            bttnTitle= 'add todo'
        else: 
            delStatus = False
            bttnTitle= 'update todo'

        addStatus = False

        if optCol.button( 'Delete',
            disabled=delStatus,
            use_container_width= True,
            key= f'TodoDelete{todo.tid}'):
            res = deleteTodo( pid, todo.tid, st.session_state.auth['token'] )
            if res['status']:
                st.success( res['msg'] , icon='✅')    
                st.session_state.refreshData['project'] = True
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Failed to ad new task!",icon="⚠")


        if addCol.button( bttnTitle,
            disabled= addStatus,
            type="primary",    
            use_container_width= True):
            
            if not newTodo.tid:
                res = insertTodo( pid, st.session_state.auth['token'], newTodo )
                if res['status']:    
                    st.success( res['msg'] , icon='✅')    
                    st.session_state.refreshData['project'] = True
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to ad new task!",icon="⚠")
                
            else:
                st.write("update")
                res = updateTodoStatusDesc( pid,
                                           newTodo.tid,
                                           newTodo.description,
                                           newTodo.status,
                                           st.session_state.auth['token']
                                           )
                if res['status']:    
                    st.success( res['msg'] , icon='✅')    
                    st.session_state.refreshData['project'] = True
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to ad new task!",icon="⚠")