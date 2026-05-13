# Opportunity App

## 🧰 Setup Instructions

### 1. Create and Activate the Virtual Environment
First, create a virtual environment (if not already created) and activate it.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies
After activating the virtual environment, install all required libraries:
```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing or needs updating, follow the steps below.

---

### 3. Generate or Update `requirements.txt`
To record all installed packages so others can recreate your environment:
```bash
pip freeze > requirements.txt
```

If you add new libraries later, rerun this command to update the file.  
Other team members can then install all dependencies with:
```bash
pip install -r requirements.txt
```

---

### 4. Start the Server
Run the Django development server:
```bash
python manage.py runserver
```

Then open your browser and navigate to:  
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 👤 Test Accounts

| Role | Email | Password |
|------|--------|-----------|
| Student | student_oppo@drew.edu | 1Opportunity! |
| Organization | org_oppo@drew.edu | 1Opportunity! |
| Administrator | admin_oppo@drew.edu | 1Opportunity! |

---

## ⚙️ Admin Panel

Access the Django admin interface here:  
👉 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

**Superuser Credentials**
- **Email:** `super_oppo@drew.edu`  
- **Username:** `super_oppo`  
- **Password:** `1OpportunityApp!`

---

## 💡 Notes
- Always activate your virtual environment before running the server.  
- Stop the server anytime with `Ctrl + C` in the terminal.  
- If dependencies change, rerun `pip freeze > requirements.txt` to update the file.  
- To ensure compatibility, use the same Python version across environments (recommended: Python 3.10+).
