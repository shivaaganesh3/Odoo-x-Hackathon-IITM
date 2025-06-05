# 🕒 Celery Scheduled Jobs Setup Guide

## Overview

This setup adds two automated email jobs to your SynergySphere platform:

1. **Daily Reminders** (8 AM daily) - Task summaries for each user
2. **Monthly Reports** (1st of month) - Activity reports with charts

## 📋 Prerequisites

### 1. Install Redis Server

**Windows:**
```bash
# Download and install Redis from: https://github.com/tporadowski/redis/releases
# Or use Docker:
docker run -d -p 6379:6379 redis:alpine
```

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Email Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Gemini API (existing)
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings > Security > App passwords
3. Generate an app password for "Mail"
4. Use this password in `SMTP_PASSWORD` (not your regular password)

## 🚀 Running the Jobs

### Option 1: Using the Startup Script (Recommended)

```bash
cd backend
python start_celery.py
```

This starts both worker and beat scheduler.

### Option 2: Manual Commands

**Terminal 1 - Worker:**
```bash
cd backend
celery -A celery_app:celery worker --loglevel=info --concurrency=2
```

**Terminal 2 - Beat Scheduler:**
```bash
cd backend
celery -A celery_app:celery beat --loglevel=info
```

## 🧪 Testing the Jobs

### Manual Job Triggers

```bash
# Test daily reminders
celery -A celery_app:celery call scheduled_jobs.test_daily_reminders

# Test monthly reports  
celery -A celery_app:celery call scheduled_jobs.test_monthly_reports
```

### Check Job Status

```bash
# Monitor active tasks
celery -A celery_app:celery inspect active

# View scheduled tasks
celery -A celery_app:celery inspect scheduled
```

## 📅 Schedule Configuration

The jobs are configured in `celery_app.py`:

```python
beat_schedule={
    'daily-task-reminders': {
        'task': 'scheduled_jobs.send_daily_reminders',
        'schedule': 60.0 * 60.0 * 24.0,  # 24 hours
        # For specific time: crontab(hour=8, minute=0)
    },
    'monthly-activity-reports': {
        'task': 'scheduled_jobs.send_monthly_reports', 
        'schedule': 60.0 * 60.0 * 24.0 * 30.0,  # 30 days
        # For 1st of month: crontab(hour=9, minute=0, day_of_month=1)
    },
}
```

### Setting Specific Times

Uncomment the `crontab` lines to set exact times:

```python
from celery.schedules import crontab

# Daily at 8 AM UTC
'schedule': crontab(hour=8, minute=0)

# Monthly on 1st at 9 AM UTC  
'schedule': crontab(hour=9, minute=0, day_of_month=1)
```

## 📧 Email Templates

### Daily Reminder Features:
- ✅ Overdue tasks (red highlight)
- ✅ Due today tasks (orange highlight)  
- ✅ Upcoming tasks (green highlight)
- ✅ Task counts summary
- ✅ Project and priority info

### Monthly Report Features:
- ✅ Completion metrics
- ✅ Average completion time
- ✅ Active projects list
- ✅ Pie chart (if matplotlib available)
- ✅ Status breakdown

## 🔧 Troubleshooting

### Common Issues

**Redis Connection Failed:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Email Not Sending:**
- Verify SMTP credentials in `.env`
- Check Gmail app password (not regular password)
- Ensure 2FA is enabled for Gmail

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check celery installation
celery --version
```

**No Tasks in Queue:**
- Verify beat scheduler is running
- Check `celery_app.py` configuration
- View logs for error messages

### Logs and Monitoring

```bash
# View worker logs
celery -A celery_app:celery worker --loglevel=debug

# Monitor Redis queues
redis-cli monitor

# Check task results
celery -A celery_app:celery result task-id-here
```

## 📊 Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/celery -A celery_app:celery worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/celery-beat.service`:

```ini
[Unit]  
Description=Celery Beat
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/celery -A celery_app:celery beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
```

### Docker Deployment

Add to your `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  celery-worker:
    build: .
    command: celery -A celery_app:celery worker --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
  
  celery-beat:
    build: .
    command: celery -A celery_app:celery beat --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
```

## 🎯 Customization

### Adding New Scheduled Jobs

1. Create task function in `scheduled_jobs.py`:
```python
@celery.task(bind=True)
def my_custom_job(self):
    # Your job logic here
    return "Job completed"
```

2. Add to beat schedule in `celery_app.py`:
```python
'my-custom-job': {
    'task': 'scheduled_jobs.my_custom_job',
    'schedule': crontab(hour=10, minute=30),  # 10:30 AM daily
},
```

### Email Template Customization

Edit the HTML templates in `render_daily_reminder_email()` and `render_monthly_report_email()` functions in `scheduled_jobs.py`.

## 🚦 Status Check

Verify everything is working:

```bash
# 1. Check Redis
redis-cli ping

# 2. Check Celery worker
celery -A celery_app:celery inspect ping

# 3. Test email job
celery -A celery_app:celery call scheduled_jobs.test_daily_reminders

# 4. Monitor logs
tail -f celery.log
```

**🎉 You're all set! Your scheduled email jobs are now active.** 