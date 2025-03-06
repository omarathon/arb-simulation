# Sports Betting Arbitrage Bot Simulation

![image](https://github.com/user-attachments/assets/e20f4127-7fe3-4fee-acb8-192214cb79cb)

Author: Omar Tanner

# Requirements for running locally

## OS

Built in Ubuntu (running on WSL) but the app should work on Windows/Mac too.

## Software

1. Python 3 (`python --version == 3.10.12`)
    1. https://www.python.org/downloads/
1. Node.js and npm  (`npm --version == 10.8.1`)
    1. https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
1. Docker (`docker --version == 26.1.1`)
    1. https://docs.docker.com/engine/install/


# Workflows

## Running locally

You will need to run both the frontend and backend locally to fully run the app.

⚠️ **Note:** ports `3000` and `8000-8005` must be free.

### Backend

Run from the root of the repository:

1. `docker-compose -f docker-compose.yml up --build -d`

This will run the backend in detached mode in docker. If you would like to run it in attached mode (e.g. to see the logs), remove the `-d`.

### Frontend

Run from the root of the repository:

1. `cd frontend`
1. `npm install`
1. `npm start`

## Testing locally

### Backend (28 tests)

Run from the root of the repository:

1. Make a new venv:
    1. `python -m venv venv`
    1. `source venv/bin/activate`
1. Install requirements:
    1. `pip install -r backend/requirements.txt`
1. Run tests
    1. `pytest backend`

### Frontend (15 tests)

Run from the root of the repository:

1. `cd frontend`
1. `npm install`
1. `npm test -- --watchAll`
