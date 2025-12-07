# US Time Backend

This is the backend part of the US Time app. It provides the API for the frontend to get data about mental health assessments and disorders.

## What it does

- Store and manage mental health assessment questions
- Save user assessment answers
- Provide information about mental health disorders
- Handle search for disorders

## How to run

1. Make sure you have Python installed
2. Open a terminal in this folder
3. Run `pipenv install` to install packages
4. Run `pipenv run python app.py` to start the server
5. The API will be available at http://localhost:8000

## Tech used

- SQLAlchemy for database
- Alembic for database migrations
- Pipenv for managing packages
