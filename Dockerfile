# Use a lightweight Python image
FROM python:3.12.2-slim

# Set the working directory
WORKDIR /app

# Copy only dependency files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install pip and PDM
RUN pip install --upgrade pip && pip install pdm

# Install project dependencies (production only)
#RUN PDM_VENV_IN_PROJECT=1 pdm config python.use_venv false && pdm install --prod

# Copy the rest of the application code
COPY . .

# Make sure the start script is executable
RUN chmod +x ./start.sh

# Expose the application port
EXPOSE 8000

# Start the app
CMD ["sh", "./start.sh"]
