# Use lightweight Python image (no Playwright needed)
FROM apify/actor-python:3.11

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . ./

# Run the Actor
CMD ["python", "-m", "src"]
