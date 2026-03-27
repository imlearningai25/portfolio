# Niraj Byanjankar — Portfolio Website

A professional portfolio built with **Flask**, featuring a dark tech theme, animated sections, and a working Gmail contact form. Deployable locally or via **Docker**.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Gmail Setup (Contact Form)](#gmail-setup)
3. [Option A — Run Locally (no Docker)](#option-a--run-locally)
4. [Option B — Docker (Recommended)](#option-b--docker)
5. [Option C — Docker Compose (Production)](#option-c--docker-compose)
6. [Environment Variables](#environment-variables)
7. [Deploying to a Cloud Server](#deploying-to-a-cloud-server)

---

## Project Structure

```
portfolio/
├── app.py                  ← Flask app, routes, Flask-Mail config
├── requirements.txt        ← Python dependencies (incl. Gunicorn)
├── Dockerfile              ← Multi-stage Docker build
├── docker-compose.yml      ← Compose for easy start/stop
├── .dockerignore           ← Files excluded from the Docker image
├── .env.example            ← Template for your secrets
├── .env                    ← Your actual secrets (never commit this!)
├── templates/
│   ├── base.html           ← Navbar, footer, shared layout
│   └── index.html          ← All portfolio sections
└── static/
    ├── css/style.css       ← Dark tech theme + responsive
    └── js/main.js          ← Typing animation, AOS, contact form
```

---

## Gmail Setup

The contact form sends email to your Gmail inbox via **SMTP App Password** (no OAuth needed).

**Steps:**
1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (required to use App Passwords)
3. In the search bar, type **"App Passwords"** and open it
4. Select **App: Mail** → **Device: Other (Custom name)** → type `Portfolio`
5. Click **Generate** — Google will show a **16-character password**
6. Copy it (remove spaces) and use it as `GMAIL_APP_PASSWORD` in your `.env`

---

## Option A — Run Locally

**Requirements:** Python 3.9+

```bash
# 1. Clone / navigate to the project folder
cd portfolio

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in GMAIL_USER, GMAIL_APP_PASSWORD, SECRET_KEY

# 5. Run the development server
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Option B — Docker

**Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Build the image

```bash
cd portfolio

# Build the image (only needed once, or after code changes)
docker build -t niraj-portfolio .
```

### Run the container

```bash
docker run -d \
  --name niraj_portfolio \
  --restart unless-stopped \
  -p 5000:5000 \
  -e GMAIL_USER=nirajbjk@gmail.com \
  -e GMAIL_APP_PASSWORD=your_16char_password \
  -e SECRET_KEY=your-secret-key-here \
  niraj-portfolio
```

Open **http://localhost:5000** in your browser.

### Useful Docker commands

```bash
# Check container status
docker ps

# View live logs
docker logs -f niraj_portfolio

# Stop the container
docker stop niraj_portfolio

# Remove the container
docker rm niraj_portfolio

# Rebuild after code changes
docker build -t niraj-portfolio . && docker restart niraj_portfolio
```

---

## Option C — Docker Compose

The easiest way to manage the app in production. Docker Compose reads your `.env` file automatically.

**Requirements:** Docker Desktop (includes Compose) or `docker compose` CLI.

### First-time setup

```bash
cd portfolio

# 1. Create your .env file
cp .env.example .env
# Fill in GMAIL_USER, GMAIL_APP_PASSWORD, and SECRET_KEY

# 2. Build and start everything
docker compose up -d --build
```

Open **http://localhost:5000** in your browser.

### Day-to-day commands

```bash
# Start the app
docker compose up -d

# Stop the app
docker compose down

# View logs
docker compose logs -f

# Rebuild after code changes and restart
docker compose up -d --build

# Check status
docker compose ps
```

### Changing the port

To serve on port **80** instead of **5000**, edit `docker-compose.yml`:

```yaml
ports:
  - "80:5000"       # host port 80 → container port 5000
```

---

## Environment Variables

| Variable              | Required | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| `GMAIL_USER`          | Yes      | Your Gmail address (e.g. `nirajbjk@gmail.com`)   |
| `GMAIL_APP_PASSWORD`  | Yes      | 16-char Gmail App Password (no spaces)           |
| `SECRET_KEY`          | Yes      | Random string for Flask session signing          |

Copy `.env.example` to `.env` and fill in these values. **Never commit `.env` to Git.**

---

## Deploying to a Cloud Server

### Google Cloud Run (serverless, no server management)

```bash
# Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build & push image to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/niraj-portfolio

# Deploy to Cloud Run
gcloud run deploy niraj-portfolio \
  --image gcr.io/YOUR_PROJECT_ID/niraj-portfolio \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GMAIL_USER=nirajbjk@gmail.com,GMAIL_APP_PASSWORD=xxx,SECRET_KEY=xxx
```

### Any Linux VPS (DigitalOcean, AWS EC2, Linode, etc.)

```bash
# 1. Install Docker on your server
curl -fsSL https://get.docker.com | sh

# 2. Copy your project files to the server
scp -r ./portfolio user@your-server-ip:/home/user/portfolio

# 3. SSH into the server
ssh user@your-server-ip

# 4. Create .env and start with Docker Compose
cd portfolio
nano .env          # fill in your values
docker compose up -d --build

# 5. (Optional) Open port 5000 in your firewall
sudo ufw allow 5000
```

> **Tip:** For a production domain with HTTPS, uncomment the Nginx block in `docker-compose.yml` and configure Let's Encrypt SSL certificates.

---

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| Backend    | Python 3.11, Flask 3.0        |
| WSGI       | Gunicorn (production server)  |
| Email      | Flask-Mail + Gmail SMTP       |
| Frontend   | HTML5, CSS3, Vanilla JS       |
| Fonts      | Inter, JetBrains Mono         |
| Icons      | Font Awesome 6                |
| Container  | Docker (multi-stage build)    |
| Orchestration | Docker Compose             |
