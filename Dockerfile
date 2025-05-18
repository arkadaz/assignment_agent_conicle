FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl gnupg ca-certificates \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxss1 libdbus-1-3 libxext6 libxfixes3 libxrender1 libgtk-3-0 xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Pin Chrome version to match your detected Chrome version
ENV CHROME_VERSION=136.0.7103.94

# Install pinned Chrome version
RUN wget -O chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" && \
    unzip chrome-linux64.zip -d /opt/chrome-for-testing && \
    rm chrome-linux64.zip && \
    ln -sf /opt/chrome-for-testing/chrome-linux64/chrome /usr/local/bin/google-chrome

# Install matching ChromeDriver version using the new URL format
RUN wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 && \
    chmod +x /usr/local/bin/chromedriver

# Install Python deps
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy app files
COPY agent.py .
COPY tools.py .
COPY models.py .
COPY ui_streamlit.py .
COPY settings.py .
COPY vector_db.py .
COPY README.md .
COPY data/ ./data/

EXPOSE 8080

CMD ["streamlit", "run", "ui_streamlit.py", "--server.port=8080"]