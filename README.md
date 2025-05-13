# 🚀 Full Stack Search Engine App with FastAPI & React (Vite)

This project is a monorepo that includes:

- ⚙️ **FastAPI** backend (in `/backend`)
- 🌐 **React (Vite)** frontend (in `/frontend`)
- 🐳 Managed using **Docker Compose**

---

## 📦 Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🔧 Project Structure

project/  
├── backend/  
│ ├── main.py  
│ └── ...  
├── frontend/  
│ ├── src/  
│ ├── .env  
│ └── ...  
├── docker-compose.yml  
└── README.md  


---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Build and run the containers

```bash
docker-compose up --build
```

🛠️ To rebuild without cache:

```bash
docker-compose build --no-cache
docker-compose up
```

### 🌍 Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000  

### 🐞 Troubleshooting  
Ensure your backend is listening on 0.0.0.0, not localhost.

Make sure ports 3000 and 8000 are not used by other apps.

Use docker-compose logs -f to monitor service logs.


