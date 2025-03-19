FROM python:3.12-slim

RUN apt update
RUN apt install -y git

RUN apt update -y
RUN apt upgrade -y
RUN apt install -y curl sqlite3
RUN curl -fsSL https://ollama.com/install.sh | sh

# Run ollama serve
# # While the app is running, in another terminal, run the following command to pull the model
# RUN ollama pull llama3.2
