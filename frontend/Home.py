import streamlit as st
from forms import loginForm, createProjectContainer, projectList, logout, alertLogout
from reqs import userProfile, userProjects, HttpException
import time
import streamlit.components.v1 as components


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
        'tokenExpr' : False
    }

#============================================================
# MAIN - Function
#============================================================
    
def main() -> None:
        
    if not st.session_state.auth['token']:
        
        if st.session_state.refreshData['tokenExpr']:
            # token expire alert
            st.toast("Your token expired. Login again use the service again",
                     icon=':material/Notifications_Active:')
            st.session_state.refreshData['tokenExpr'] = False
        

        loginForm()
        
    else:
        
        st.title('Projects.',anchor=False)        
        
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
            time.sleep(0.5)
               
        if st.session_state.projects:       
            with st.container(border=False):
                projectList(st.session_state.projects)
  
        else:
            
            Caption = f" **Hello :rainbow[{st.session_state.auth['username']}!]** \
            Your project list are empty. please create a project"
            
            cptin, mopt = st.columns([3, 1], 
                                                gap= 'small',
                                                vertical_alignment='bottom')
            
            cptin.info( Caption )

                
            if mopt.button(":material/logout:",
                        use_container_width=True,
                        help="Logout :material/logout:"):
                alertLogout()

            createProjectContainer(True)  

    
if __name__ == "__main__":
    
    try:
        main()
        
    except KeyError:
        st.error('Encountered a small error.',icon=":material/error:")
        time.sleep(1)
        if st.button('Rerun applcation'):
            st.rerun()
        
    except HttpException as e:
        st.error(f"HTTP Error {e.status_code}: {e.message}", icon="🌐")
        logout()
        if st.button('Rerun applcation'):
            st.rerun()        

    except Exception as e:
        print("Exception Occured at main:",e)
        st.warning(e,icon='☠')
        logout()
        if st.button('Rerun applcation'):
            st.rerun()
            
    finally:
        
        components.html("""
        <script>
        window.onbeforeunload = function() {
            return 'Are you sure you want to leave? You might lose unsaved data.';
        };
        </script>
        """, height=0)