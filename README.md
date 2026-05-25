
```
backend
├─ .qodo
│  ├─ agents
│  └─ workflows
├─ app
│  ├─ api
│  │  └─ routes
│  │     ├─ auth.py
│  │     ├─ resume.py
│  │     └─ scan.py
│  ├─ auth
│  │  ├─ dependencies.py
│  │  ├─ jwt_handler.py
│  │  └─ password.py
│  ├─ core
│  │  ├─ config.py
│  │  ├─ database.py
│  │  └─ dependencies.py
│  ├─ main.py
│  ├─ models
│  │  ├─ chunk.py
│  │  ├─ resume.py
│  │  ├─ scan.py
│  │  └─ user.py
│  ├─ services
│  │  ├─ rag_service.py
│  │  ├─ resume_service.py
│  │  └─ search_service.py
│  └─ utils
│     ├─ hash.py
│     └─ score.py
├─ create_tables.py
├─ requirements.txt
└─ run.py

```