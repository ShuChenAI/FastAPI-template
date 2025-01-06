#!/bin/bash

# docker compose file
TARGET_FILE=$1
if [ -z "${TARGET_FILE}" ]; then
  echo "Error: Please provide the docker-compose file as the first argument."
  exit 1
fi

# Pull the latest changes from the main branch
# Uncomment the following line if you want the script to include the pull step
git pull origin main

# Check if src/database/models.py was modified
# shellcheck disable=SC1083
git diff --name-only HEAD@{1} HEAD | grep src/database/models.py

# if so, run the Alembic revision command
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
  echo "True: src/database/models.py was modified."

  # Get the current date in a specific format
  current_date=$(date +"%Y-%m-%d %H:%M:%S")

  # Run the Alembic revision command with a custom message that includes the current date
  docker compose -f "${TARGET_FILE}" exec backend alembic revision --autogenerate -m "revision generated on ${current_date}"
  docker compose -f "${TARGET_FILE}" exec backend alembic uprade head

  # git add to stage the changes
  git add ./*.alembic
  git commit -m "Alembic revision generated on ${current_date}"
  git push origin main
else
  echo "False: src/database/models.py was NOT modified."
fi
