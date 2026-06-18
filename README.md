# LifeBot AI Web App 💬

LifeBot is a modern, responsive, and minimalist AI chat web application. Inspired by the ChatGPT interface, it features a sleek dark mode design with a completely independent sidebar, auto-expanding text areas, and smooth chat animations.

## 🌟 Features

- **Modern UI/UX:** A premium dark theme (black/gray/white) with glassmorphism touches and smooth transitions.
- **Responsive Layout:**
  - **Desktop:** Full-height (100vh) split view with an independent collapsible sidebar and a scrolling chat window.
  - **Mobile:** A sliding drawer sidebar with a dark overlay for smaller screens.
- **Smart Chat Interface:**
  - Auto-expanding message input box (up to a defined maximum height).
  - Smooth auto-scrolling to the latest message.
  - "Typing..." animations (pulsing dots) while waiting for the AI response.
  - Smart send button that disables itself when the input is empty.
- **Chat Management:** Create new chats, rename existing chat titles, and delete old conversations.
- **User Authentication:** Secure user registration, login, and session management system.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy (SQLite)
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (jQuery for AJAX requests)
- **Icons:** FontAwesome

## 🚀 Installation & Setup

Follow these instructions to get the project running on your local machine.

### 1. Clone the repository
```bash
git clone https://github.com/Ahmetfrkn/lifebot-ai-webapp.git
cd lifebot-ai-webapp
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
Make sure you have Flask and its dependencies installed. *(If a `requirements.txt` is added later, use `pip install -r requirements.txt`)*
```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt requests
```

### 4. Initialize the Database
Before running the application for the first time, you need to create the database tables:
```bash
python init_db.py
```

### 5. Run the Application
```bash
python app.py
```

### 6. Access the App
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## 📂 Project Structure

```text
lifebot-ai-webapp/
│
├── app.py                 # Main Flask application and routes
├── models.py              # Database models (User, Chat, Message)
├── init_db.py             # Script to initialize the SQLite database
├── instance/              # Folder containing the SQLite database
│
├── static/
│   └── css/
│       └── style.css      # Core styling, responsive layout, and dark theme
│
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Base layout wrapper
│   ├── index.html         # Main app layout (Sidebar + Chat Area)
│   ├── login.html         # User login page
│   ├── register.html      # User registration page
│   └── partials/          # Reusable UI components (header, sidebar, chat input, etc.)
│
└── .gitignore             # Git ignore file
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License
This project is for educational and personal use. All rights reserved.
