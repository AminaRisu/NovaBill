# NovaBill

**NovaBill** is a web-based **Restaurant Billing System** built with **Django**.  
It allows restaurant staff to manage items, generate bills, and view reports efficiently.

---

## 🛠 Features

- Add, edit, and manage menu items with prices  
- Generate bills for customers  
- Auto-calculated totals  
- Search items quickly with an autocomplete feature  
- Export bills as PDF (optional)  
- Daily reports for sales tracking  
- Dark-themed dashboard with intuitive UI  

---

## 📂 Project Structure

NovaBill/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── billing/ # Main app for billing functionality
├── templates/ # HTML templates
├── static/ # CSS, JS, and images
├── media/ # Uploaded files (ignored in Git)
└── venv/ # Virtual environment (ignored in Git)

yaml
Copy code

---

## ⚙ Installation

1. **Clone the repository**:  
```bash
git clone https://github.com/AminaRisu/NovaBill.git
cd NovaBill
Create a virtual environment (if not already):

bash
Copy code
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Linux/Mac
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Apply migrations:

bash
Copy code
python manage.py migrate
Run the development server:

bash
Copy code
python manage.py runserver
Open the app in your browser:

cpp
Copy code
http://127.0.0.1:8000/
👤 Usage
Login with admin credentials (create using python manage.py createsuperuser)

Add menu items, generate bills, and check reports

Use the search bar to quickly find items

📝 Notes
Uploaded files are stored in media/ and are ignored by Git.

Static files are collected in staticfiles/ (also ignored).

Remember to create superuser credentials for admin access.

📄 License
This project is licensed under the MIT License.

🎯 Future Improvements
Voice-assisted billing

Multi-user support with roles (admin, cashier)

Integration with cloud storage for reports

Mobile-friendly responsive design
