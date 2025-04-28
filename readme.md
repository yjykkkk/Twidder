# Twidder
A full-stack web application allowing users to register, manage their profiles, post messages on personal walls, and view other users' walls.

## Features
- User registration and authentication (password hashing with bcrypt)
- Profile management and wall messaging
- Real-time session handling via WebSocket (auto logout on multiple sessions)
- SQLite database backend
- Automated end-to-end testing with Selenium
- Deployed on Heroku for live demonstration

## Tech Stack
- Backend: Python, Flask, Flask-Sock
- Frontend: HTML, CSS, Vanilla JavaScript
- Database: SQLite
- Authentication: bcrypt password hashing
- Testing: Selenium (E2E tests)
- Deployment: Heroku with Gunicorn WSGI server

## How to execute
```shell
gunicorn -w 1 -k gevent server:app  
```
