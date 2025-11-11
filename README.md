# Network - CS50 Web Project

A mini social network built with Django and JavaScript, where users can register, log in, create posts, follow other users, like posts, and comment in real time. Designed to be simple, modern, and responsive.

---

## Features

- User authentication (Register, Login, Logout)
- Create, edit, and view posts
- Like/unlike posts
- Follow/unfollow other users
- View posts from followed users
- Comment on posts
- Responsive, modern design with Bootstrap and custom CSS

---

## Installation & Running Locally

1. **Clone the repository**
   git clone <your-repo-url>
   cd network

2. **Create and activate a virtual environment**
    python -m venv venv
    source venv/bin/activate    # Linux/macOS
    venv\Scripts\activate       # Windows

3.  **Install dependencies**
     pip install -r requirements.txt

4.  **Run database migrations**
    python manage.py makemigrations
    python manage.py migrate

5.  **Start the development server**
    python manage.py runserver

6.  **Open your browser**
    Go to: http://127.0.0.1:8000/

**Usage**

Register a new user account

Create posts on the homepage

Like and comment on posts

Follow other users and see their posts in your feed

Edit your own posts

All features update dynamically using AJAX for a smooth experience

Technologies Used

Backend: Django 4.x

Frontend: HTML, CSS, JavaScript, Bootstrap 4/5

Database: SQLite (default)

AJAX: For like, follow, comment, and edit actions

Notes

Ensure JavaScript is enabled in your browser for AJAX features

Tested on both desktop and mobile browsers

Modern UI with hover effects and responsive layout

Fully functional with CS50 Web requirements

Author

BTECH - Beloved Technology
Built with 💙 by BTECH