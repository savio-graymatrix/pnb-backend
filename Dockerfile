# Use the appropriate base image
FROM python:3.12.2-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Sync dependencies (assuming PDM is used)
RUN pip install pdm

# Make sure start.sh is executable
RUN chmod +x ./start.sh

# Expose the port your app runs on
EXPOSE 8000

# Use the shell form for CMD to execute the script
CMD ["sh", "./start.sh"]
