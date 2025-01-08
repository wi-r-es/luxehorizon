# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the project code into the container
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the Django server when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]