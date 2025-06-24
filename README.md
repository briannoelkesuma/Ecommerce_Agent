# 🛒 Ecommerce_Agent

**Ecommerce_Agent** is an Ecommerce AI project for Tershine products where intelligent agents are built and tailored to e-commerce stores. It provides a modular structure for backend logic, database management, and conversational sales agent workflows — with built-in Streamlit integration for rapid prototyping.
---

## ✨ Features

- 🧱 Modular architecture (backend, database, sales agent)
- 🖼 Static asset support (images, configs)
- 🧪 Scripts for testing and database setup
- 📦 Streamlit-compatible structure for UI integration
- 💾 Persistent profile and configuration management

---

## 📁 Project Structure

```
Ecommerce_Agent/
├── .streamlit/                 # Streamlit configuration files
├── archive/                    # Archived or legacy code
├── assets/                     # Static assets (e.g., images)
├── backend/                    # Backend logic and API modules
├── database/                   # Database models and setup scripts
├── docs/                       # Documentation files
├── path/to/persistent/profile/ # Persistent user/profile data for chromium profile
├── sales_agent/                # Sales agent logic and workflows
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── __init__.py                 # Package initializer
├── creds.json                  # Credential/configuration file
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── setup_database.py           # Script to set up the database
├── test.py                     # Test script
```

---

## 📁 Code Repository Diagram and Flow
![GitDiagram (1)](https://github.com/user-attachments/assets/8acdc1ef-ee79-437f-b88b-216642c99bd4)


## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/briannoelkesuma/Ecommerce_Agent.git
cd Ecommerce_Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up the Database to insert tershine's product which were scraped already into products_path=str(BASE_DIR / "database" / "db" / "products.json").

```bash
python setup_database.py
```

### 4. Run the Frontend Application

```bash
streamlit run frontend/app.py
```

### 5. Run the Backend Application

```bash
cd backend 
python app.py
```

---
