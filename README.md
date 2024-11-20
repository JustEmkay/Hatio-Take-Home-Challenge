

# Project Management Application
This project is a web-based application for managing projects and tasks (todos). Users can create projects, manage todos, and export project summaries as GitHub gists or markdown files.

## Features
1. User Authentication:
- Register and log in with secure credentials.
2. Project Management:
- Create, view, edit, and delete projects.
3. Todo Management:
- Add, update, delete, and manage the status (pending/completed) of todos.
4. Export Project Summary:
- Export project details as a secret GitHub gist or download as a markdown file.
5. Modern Frontend:
- Built with Streamlit for a simple, user-friendly interface.

## Setup Instructions
### Prerequisites
* Python 3.10 or higher
* pip (Python package installer)

### Installation Steps
1. Clone the Repository:

* [git clone](https://github.com/JustEmkay/Hatio-Take-Home-Challenge.git)
* ```cd <your-repository-directory>```

2. Set Up a Virtual Environment (Optional but Recommended):

```
python -m venv venv 
source venv/bin/activate  # On Windows:env\Scripts\activate
```
3. Install Dependencies:

```pip install -r requirements.txt```

4. Set Up the SQLite Database: 
Ensure the database file path in ```manager.py``` matches your setup.
The default path is```database/hatio_todo.db ```

5. Run the Backend Server:
```
cd api
uvicorn server:app --reload
```
6. Run the Frontend Application:
```
cd frontend
streamlit run home.py
```
## Usage Instructions

1. Start the Application:
* Open your browser and navigate to ```http://localhost:8501``` for the frontend and ```http://127.0.0.1:8000/docs``` for the backend API documentation.

2. Register and Login:
* Use the registration form to create a new account.
* Log in with your credentials.

3. Project Management:

* Create a new project with a title and todos.
* View, edit, or delete projects from the project list.

4. Todo Management:

* Add new todos to a project.
* Update their description or status (pending/completed).
* Delete unwanted todos.

5. Export Project Summary:

* Export your project summary as a GitHub gist or download it as a markdown file.


* https://github.com/user-attachments/assets/7f5e20f2-a67e-4606-b821-92c131df8534

* gist api resquest Code:
```
def createGithubGist(access_token: str, filename: str, content: str, description: str, isPublic: bool) -> dict:
    # return html_url and id of created gist.

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
            'status': True,
            'url': resp.json().get('html_url'),
            'id': resp.json().get('id')
        }
    else:
        return {
            'status': False,
            'msg': resp.text
        }

```


## Directory Structure

```
.
├── api/                 
│   ├── database/             # SQLite database directory
│   │   └── hatio_todo.db     # SQLite database
│   ├── server.py             # FastAPI backend       
│   └── manager.py            # Database management
├── frontend/            
│   ├── forms.py              # Frontend components and forms 
│   ├── home.py               # Streamlit frontend entry point
│   ├── schema.py             # Pydantic models
│   └── reqs.py               # API requests handling
├── requirements.txt          # Dependencies

```
## API Documentation
- The FastAPI backend provides a Swagger UI interface for API exploration:
- Visit ```http://127.0.0.1:8000/docs```

## Important Notes
1. GitHub Gist Integration:

- Ensure you generate a GitHub personal access token to export summaries as gists.
- Configure the token in the Streamlit interface during gist export.

2. Session Management:

- User authentication is token-based with a 6-hour expiry.
- Logout automatically clears session data.

3. Database Setup:

- The application uses SQLite. Modify the database path in manager.py if necessary.




