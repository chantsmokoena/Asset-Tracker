
# AssetTrack — IT Asset Management System

**Portfolio Project | Chantel Hlongwane**

A full-stack IT asset management system demonstrating CRUD operations, REST API design, and frontend development.

## 🧰 Tech Stack

|Layer      |Technology                                    |
|-----------|----------------------------------------------|
|Frontend   |HTML5, CSS3, Vanilla JavaScript               |
|Backend API|Python 3.11, FastAPI                          |
|Database   |SQLite (via Python sqlite3)                   |
|Deployment |GitHub Pages (frontend) + Railway/Render (API)|

## 🚀 Run Locally

### Frontend (no setup needed)

Just open `index.html` in your browser — it works standalone with localStorage.

### Backend API

```bash
pip install -r requirements.txt
python main.py
```

API docs available at: `http://localhost:8000/docs`

## 📡 API Endpoints

|Method|Endpoint      |Description                                              |
|------|--------------|---------------------------------------------------------|
|GET   |`/assets`     |List all assets (supports ?status=, ?category=, ?search=)|
|POST  |`/assets`     |Register new asset                                       |
|GET   |`/assets/{id}`|Get single asset                                         |
|PATCH |`/assets/{id}`|Update asset fields                                      |
|DELETE|`/assets/{id}`|Remove asset                                             |
|GET   |`/stats`      |Asset statistics summary                                 |

## 💡 Features

- Full CRUD — create, read, update, delete assets
- Filter by status and category
- Live search across name, department, serial number
- Stats dashboard (total, allocated, maintenance, decommissioned)
- Responsive design, dark theme

## 👩🏾‍💻 Author

**Nontokozo Chantel Hlongwane** | BI Developer → Software Developer  
[LinkedIn](https://www.linkedin.com/in/chantel-hlongwane-817a391b1/) | [Portfolio](https://chantsmokoena.github.io/)
