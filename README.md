# CITS3403 - Web-Application Project

## Game Name:
### Technoanimal Runner

## Propose of the Application:
This application is a browser-based multiplayer game built with Flask. The purpose of the project is to provide an engaging and interactive web-based gaming experience while demonstrating client-server web development concepts such as authentication, persistent databases, user interaction, and dynamic gameplay systems.

## Design and Use:
The application follows a client-server architecture using Flask as the backend framework and SQLite with SQLAlchemy for persistent data storage.
The frontend uses HTML templates, JavaScript, Tailwind CSS, and custom CSS styling to provide a responsive neon-themed interface.
The application is divided into multiple components:
- Authentication system for signup, login, email verification, and password reset
- Profile management system for editing user information
- Leaderboard system for displaying player rankings and scores
- Gameplay system developed with JavaScript
- Friends and sabotage systems for player interaction
- Persistent database storage using SQLAlchemy models and migrations

Users can:
- create accounts and securely log in
- verify their email
- reset forgotten passwords
- play the game and save scores
- edit their profile
- view leaderboard rankings
- interact with other users through gameplay features

## Team Members:
markdown| UWA ID | Name | GitHub Username |
|----------|-------------------|------------------|
| 24147733 | Evan Miocevich | Games4Doritos |
| 24439408 | Siyu Zhu | LZhuSY |
| 24991367 | Veerjot Kaur | cyber-veerjot |
| 23112189 | Evan Caraiscos | EvanCaraiscos |

## Technologies Used
- Python
- Flask
- SQLite
- SQLAlchemy
- Flask-WTF
- Flask-Login
- Flask-Migrate
- HTML
- CSS
- JavaScript
- Tailwind CSS

## Installation Instructions:


## Running Tests:
### Unit Tests:

### Selenium Tests:


## Application Features:
### Authentication System:
- User registration and login
- Secure password hashing
- Email verification system
- Password reset functionality
- Session management with Flask-Login

### Profile System:
- Create and edit user profiles
- Username customisation
- Persistent player statistics
- Friend code system

### Gameplay Features:
- Endless runner gameplay
- Dynamic score and currency system
- Persistent game statistics
- Sabotage debuff system
- JavaScript-based gameplay mechanics

### Social Features:
- Friend request system
- Friend management
- Bonus gifting interactions

### Leaderboard System:
- Global leaderboard rankings
- Persistent high score tracking
- Statistics display

## Database Models:
The application uses SQLAlchemy models for persistent storage:
- Account
- Profile
- BestStats
- Friendship

## Security Features:
- Password hashing using Werkzeug
- CSRF protection using Flask-WTF
- Login protection with Flask-Login
- Input validation and form validation
- Protected authenticated routes

## Project Structure:
app/
├── routes/
├── templates/
├── static/
├── tests/
│   ├── unit/
│   └── selenium/
├── models.py
├── forms.py
├── config.py

## Testing Coverage:
The project includes:
- Unit tests for authentication, profiles, and leaderboard functionality
- Selenium browser tests for frontend behaviour and navigation
- Validation tests for protected routes and profile editing



