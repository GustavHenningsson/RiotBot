# DietPi Cron Job Setup for Auto-Deploy

This guide will help you set up a daily cron job on your DietPi to automatically pull the latest changes from GitHub and redeploy the RiotBot Docker container.

## Setup Instructions

### 1. Copy the script to your DietPi

First, transfer the `deploy-cron.sh` script to your DietPi. You can do this by either:

**Option A: Copy from local to DietPi (if you have access)**
```bash
scp deploy-cron.sh pi@your-dietpi-ip:/home/dietpi/RiotBot/
```

**Option B: Pull from repository**
If the script is already committed to your repo, just pull it on the DietPi:
```bash
cd /home/dietpi/RiotBot
git pull
```

### 2. Make the script executable

SSH into your DietPi or access it directly, then run:
```bash
chmod +x /home/dietpi/RiotBot/deploy-cron.sh
```

### 3. Test the script manually

Before setting up the cron job, test the script to ensure it works:
```bash
cd /home/dietpi/RiotBot
./deploy-cron.sh
```

Check the log file to see if it worked:
```bash
cat /home/dietpi/RiotBot/deploy-cron.log
```

### 4. Set up the cron job

Open the crontab editor:
```bash
crontab -e
```

Add the following line to run the script daily at 18:00 (6:00 PM):
```
0 18 * * * /home/dietpi/RiotBot/deploy-cron.sh
```

Save and exit the editor (in nano: Ctrl+X, then Y, then Enter).

### 5. Verify the cron job

Check that your cron job was added successfully:
```bash
crontab -l
```

You should see the line you just added.

## How It Works

- **Schedule**: Runs every day at 18:00
- **Check for updates**: The script fetches from `origin/main` and compares with local HEAD
- **Only deploys if needed**: If no changes are detected, it exits early
- **Logs everything**: All output is logged to `/home/dietpi/RiotBot/deploy-cron.log`
- **Full rebuild**: If updates are found, it rebuilds the container with `--no-cache`

## Monitoring

To check the cron job logs:
```bash
tail -f /home/dietpi/RiotBot/deploy-cron.log
```

To check recent cron job executions:
```bash
grep CRON /var/log/syslog | tail -20
```

## Troubleshooting

### Script doesn't run
- Check cron service is running: `systemctl status cron`
- Verify crontab syntax: `crontab -l`
- Check system logs: `grep CRON /var/log/syslog`

### Permission issues
- Ensure the script is executable: `chmod +x /home/dietpi/RiotBot/deploy-cron.sh`
- Ensure the user running the cron has docker permissions: `groups $(whoami)` should show `docker`

### Docker permission errors
If you get permission errors with docker, add your user to the docker group:
```bash
sudo usermod -aG docker $USER
```
Then log out and back in.

## Disabling GitHub Actions

Since you're now using cron for deployment, you may want to disable or remove the GitHub Action to avoid conflicts. You can either:

1. Delete the `.github/workflows/deploy.yml` file
2. Disable it in GitHub repository settings under Actions
3. Keep it for manual deployment via workflow_dispatch

## Notes

- The script uses the same deployment logic as your GitHub Action
- Logs are appended, so the log file will grow over time (consider adding log rotation)
- The script only pulls from `main` branch
- A `--no-cache` build is performed to ensure fresh container builds