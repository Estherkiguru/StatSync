# StatSync

![StatSync Logo](static/image/StatSync)

StatSync is a user-friendly web application designed to streamline the process of tracking and sharing athletic performance data. Trainers can upload stats taken during training sessions, and athletes can access, view, download and share their performance data in real-time. This platform enhances communication between athletes, trainers, and recruiters, making the entire process more efficient and accessible.

## Inspiration and Background
As an athlete, I found it inconvenient to request performance updates from my trainers frequently. This led to the idea of StatSync, a streamlined platform that allows trainers to directly update athletes' stats into the system.

StatSync reduces the hassle of manual PDF creation by enabling trainers to update stats in real-time. This way, athletes, coaches, and team managers can easily assess player health and performance before games and during training sessions. This ensures that vital statistics are always up-to-date and accessible whenever needed.

StatSync is built with the goal of improving communication between trainers and athletes, and it offers an efficient solution to managing sports performance data.


## Key Features

- Athlete Dashboard: Athletes can view their stats in an organized dashboard, tracking performance metrics such as body weight, BMR, hydration level, muscle mass, and more.
- Trainer Dashboard: Trainers can log in and update the stats of their athletes, providing a seamless way to keep track of progress.
- PDF Export: Athletes can download their stats as a PDF for easy sharing with recruiters and team managers.
- User Authentication: Secure login and registration system for both athletes and trainers.
- Stat Tracking: Track various performance metrics over time to monitor and improve athletic progress.

## Getting Started
1. **Clone the repository***

git clone https://github.com/yourusername/PestSentry_api.git

cd statsync

2. **Set up a virtual environment:**
 
 python -m venv StatSync
 
 source StatSync/bin/activate

3. **Install dependencies:**

   pip install -r requirements.txt

## Usage
**Run the application**

uvicorn app:app --reload

The application will be accessible at http://127.0.0.1:8000

### Using the API
**Create a New Account:**

Register a new account for either Athletes or Trainers by navigating to the respective sign-up page.

**Log In to Your Account:**

Use your credentials to log in as an Athlete or Trainer. Upon successful login.

**Upload Stats Data (Trainer Only):**

Trainers can update or upload their athletes' stats via the Update Athlete Data endpoint. The data includes key stats like body weight, BMR, muscle mass, etc.

**View Stats Data (Athlete Only):**

Athletes can view their up-to-date training stats, which are recorded by their trainers.

**Download Stats:**

Athletes can download their stats in a PDF format through the Download Stats endpoint.

**Log Out:**

Ensure to log out after your session to clear your access token and end the session.

## Contributing

We welcome contributions to improve the StatSync API. Please follow these steps:

1. Fork the repository.

2. Create a new branch (git checkout -b feature-branch).

3. Commit your changes (git commit -am 'Add new feature').

4. Push to the branch (git push origin feature-branch).

5. Create a new Pull Request.

6. Ensure your code follows the best practices and is properly documented.

## Future Improvements:

- Integration with third-party health tracking devices for real-time data syncing.
- More advanced data visualization for better performance insights.
