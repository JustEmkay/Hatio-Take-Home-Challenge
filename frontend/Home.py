import streamlit as st
from forms import loginForm, createProjectContainer, projectList
from reqs import userProfile, userProjects
import time

#============================================================
# Streamlit Session_states
#============================================================

if 'auth' not in st.session_state: 
    st.session_state.auth = {
        'token' : {},
        'uid': None,
        'username':None,
        'email': None
    }
    
if 'projects' not in st.session_state:
    st.session_state.projects = []
    
if 'tempProject' not in st.session_state:
    st.session_state.tempProject = {
        'title' : None,
        'todos' : []
    }

if 'refreshData' not in st.session_state:
    st.session_state.refreshData = {
        'project' : False, 
    }

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
    "project": False
    
  }
})
    
#============================================================
# MAIN - Function
#============================================================
    
def main() -> None:
    

    with st.sidebar:
            if st.button("logout", use_container_width= True):
                if logout():
                    st.rerun()
            
    
    if not st.session_state.auth['token']:
        
        loginForm()
        
    else:
        
        st.title('Projects.',anchor=False)        
        placeholder = st.empty()
        
        if not st.session_state.auth['uid']:
            with st.spinner('Gathering User profile..'):
                time.sleep(1)
                userdata = userProfile(st.session_state.auth['token'])
                st.session_state.auth.update(userdata)

            if st.session_state.auth['uid']:
                with st.spinner('Gathering Project data....'):
                    time.sleep(1)
                    projectsData = userProjects(st.session_state.auth['token'])
                    st.session_state.projects = projectsData
                    st.session_state.refreshData['project'] = False
                    st.rerun()
        
        if st.session_state.refreshData['project']:
            projectsData = userProjects(st.session_state.auth['token'])
            st.session_state.projects = projectsData
            st.session_state.refreshData['project'] = False
            time.sleep(5)
               
        if st.session_state.projects:       
            with st.container(border=False):
                projectList(st.session_state.projects)
  
        else:
            createProjectContainer(True)  

    
if __name__ == "__main__":
    main()