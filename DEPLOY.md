# Deployment Guide: SonarPro Production (EC2)

Follow these steps to safely deploy the latest updates to your production instance.

## 🚀 Pre-Deployment Check
Ensure all local tests pass before pushing to `main`:
```bash
python -m pytest tests/ -v
```

## 🛠️ Deployment Steps (EC2)

1. **Connect to your EC2 instance**:
   ```bash
   ssh ubuntu@your-ec2-ip
   cd ~/redditscrapping
   ```

2. **Pull the latest changes**:
   ```bash
   git pull origin main
   ```

3. **Install/Update Dependencies**:
   New libraries (like `tiktoken`, `curl_cffi`, `pytest`) were added. Ensure they are installed:
   ```bash
   # If you use a virtualenv, activate it first
   pip install -r pyproject.toml # Or manually:
   pip install tiktoken curl_cffi pytest pytest-asyncio
   ```

4. **Restart the API Service**:
   Since the backend logic changed, you MUST restart the PM2 process:
   ```bash
   pm2 restart 0
   ```

5. **Verify Logs**:
   Check if the server started correctly and isn't throwing JWT errors:
   ```bash
   pm2 logs 0
   ```

## 🔧 Troubleshooting
- **JWT Expired Error**: If you see this, the 60s leeway added in `radar/api/auth.py` should handle most cases. If it persists, check the system time on EC2: `date`.
- **Database Locked**: If you see heavy usage, the system is already configured with WAL mode to prevent this.
