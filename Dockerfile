# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# The command to run the application will be provided at runtime
# For example, to run mcp_server_1.py, you would use:
# docker run <image_name> python mcp_server_1.py
# And for mcp_server_2.py:
# docker run <image_name> python mcp_server_2.py
CMD ["python", "src/mcp_server/mcp_server_1.py"] 