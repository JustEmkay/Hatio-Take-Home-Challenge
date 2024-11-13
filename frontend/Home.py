import streamlit as st

if 'auth' not in st.session_state: 
    st.session_state.auth = {
        'auth' : False,
        'userID': None,
        'username':None  
    }



def main() -> None:
    
    ...
    
    
if __name__ == "__main__":
    main()