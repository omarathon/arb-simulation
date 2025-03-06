# Sports Betting Arbitrage Bot Simulation

https://github.com/user-attachments/assets/78bb6821-8db8-4ce9-939b-8e2ae44e4d94

Author: Omar Tanner

# Summary

For this task, I chose to build a simulation of an arbitrage bot with a semi-realistic distrubuted backend system, and real-time visualisations on the frontend.

The backend simulates arbs by first generating odds updates according to a distribution, then detecting when odds lead to an arb, and finally simulating executing the bets for an arb by sleeping for a set duration (to simulate the time to execute the bet). In this delay, the bookmaker could've updated their price, causing either an adjustment or a cancellation (if the bookmaker closed the odd).

In a real system, the executor would actually place the bets by talking to real bookmakers, and the scraper would actually scrape bookmakers' sites. Furthermore, the backend would probably be in Rust or C++ to mininise the delay in detecting and executing arbs.





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


# Discussion (TBC)

## Architecture

![Untitled Diagram (1)](https://github.com/user-attachments/assets/d0e5f2aa-222f-4a1c-aeba-2759fd6fc82d)

## Features

## Assumptions

## Limitations

Tests - integration and E2E tests weren't implemented due to lack of time, but unit tests were implemented in the highest-priority areas concerning the core logic. On the backend, we mock Redis in the tests.

## Challenges

## If given more time
