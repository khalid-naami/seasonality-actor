FROM apify/actor-python:3.12

# Checkpoint: Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run Actor
CMD ["python3", "-m", "src.main"]
