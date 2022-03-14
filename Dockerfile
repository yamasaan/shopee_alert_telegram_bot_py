# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# ENV BOT_TOKEN=""

# Set the working directory in the container
WORKDIR /app
# Copy the dependencies
COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# Copy the content of the local src directory to the working directory
COPY . /app
# Command to run on container start
CMD ["python", "bot.py"]
