# Deployment Guide - RiotBot on Raspberry Pi

This guide covers automated deployment using Docker Compose and GitHub Actions.

## Prerequisites

- Raspberry Pi with SSH access
- Docker and Docker Compose installed on the Pi
- GitHub repository

## Initial Setup on Raspberry Pi

### 1. Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (no need for sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version

# Install Docker Compose
sudo apt install docker-compose -y
docker-compose --version
```

### 2. Clone Repository

```bash
cd /home/dietpi
git clone https://github.com/YOUR_USERNAME/RiotBot.git
cd RiotBot
```

### 3. Create .env File

```bash
cd riotbot
nano .env
```

Add your credentials:
```
GUILD=your_guild_id
BOT_TOKEN=your_bot_token
RIOT_API_KEY=your_riot_api_key
```

Save and exit (Ctrl+X, Y, Enter)

### 4. Test Local Deployment

```bash
cd /home/dietpi/RiotBot
docker-compose up -d
docker-compose logs -f  # Check logs (Ctrl+C to exit)
```

Verify the bot is online in Discord, then stop it:
```bash
docker-compose down
```

## GitHub Actions Setup

### 1. Generate SSH Key Pair

On your local computer (not the Pi):

```bash
# Generate new SSH key for deployment
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/pi_deploy

# This creates two files:
# - pi_deploy (private key) - will be added to GitHub
# - pi_deploy.pub (public key) - will be added to Pi
```

### 2. Add Public Key to Raspberry Pi

```bash
# Copy public key to Pi
ssh-copy-id -i ~/.ssh/pi_deploy.pub pi@YOUR_PI_IP

# Or manually:
cat ~/.ssh/pi_deploy.pub
# Then SSH into Pi and add it to ~/.ssh/authorized_keys
```

Test the connection:
```bash
ssh -i ~/.ssh/pi_deploy pi@YOUR_PI_IP
```

### 3. Add Secrets to GitHub

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Name | Value | Example |
|------|-------|---------|
| `PI_HOST` | Your Pi's IP address or hostname | `192.168.1.100` or `raspberrypi.local` |
| `PI_USER` | SSH username | `pi` |
| `PI_PORT` | SSH port | `22` |
| `PI_SSH_KEY` | Private key content | Copy entire content of `~/.ssh/pi_deploy` |

To get the private key content:
```bash
# On your local computer
cat ~/.ssh/pi_deploy
# Copy everything including "-----BEGIN OPENSSH PRIVATE KEY-----" and "-----END OPENSSH PRIVATE KEY-----"
```

### 4. Configure Pi Network Access

If your Pi is behind a router, you have options:

**Option A: Port Forward (Simple but less secure)**
- Forward port 22 from router to Pi
- Use router's public IP in `PI_HOST`

**Option B: Dynamic DNS (Recommended)**
- Set up DDNS service (DuckDNS, No-IP)
- Use DDNS hostname in `PI_HOST`

**Option C: VPN/Tailscale (Most secure)**
- Install Tailscale on Pi and your GitHub Actions runner
- Use Tailscale IP in `PI_HOST`

## Usage

### Automatic Deployment

Simply push to main branch:
```bash
git add .
git commit -m "Update bot"
git push origin main
```

GitHub Actions will automatically:
1. SSH into your Pi
2. Pull latest code
3. Rebuild Docker container
4. Start the bot

### Manual Deployment

Trigger from GitHub UI:
1. Go to **Actions** tab
2. Click **Deploy to Raspberry Pi**
3. Click **Run workflow**

### Monitor Deployment

Check progress:
1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. View logs in real-time

### Local Management on Pi

```bash
# View logs
docker-compose logs -f riotbot

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Start bot
docker-compose up -d

# Rebuild and restart
docker-compose up -d --build

# View container status
docker ps
```

## Troubleshooting

### SSH Connection Fails

```bash
# Test SSH from local computer
ssh -i ~/.ssh/pi_deploy pi@YOUR_PI_IP

# Check Pi's SSH service
sudo systemctl status ssh

# View GitHub Actions logs for specific error
```

### Bot Not Starting

```bash
# Check container status
docker ps -a

# View detailed logs
docker-compose logs riotbot

# Common issues:
# - Missing .env file
# - Invalid credentials in .env
# - Port conflicts
```

### Container Keeps Restarting

```bash
# Check logs for errors
docker logs riotbot --tail 50

# Usually caused by:
# - Wrong BOT_TOKEN
# - Wrong GUILD ID
# - Missing Python dependencies
```

### Deployment Succeeds but Bot Offline

```bash
# SSH into Pi and check
cd /home/dietpi/RiotBot
docker-compose ps
docker-compose logs

# Verify .env file exists and has correct values
cat riotbot/.env
```

## Maintenance

### Update Dependencies

```bash
# On Pi
cd /home/dietpi/RiotBot
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data Files

```bash
# Backup saved data
cd /home/dietpi/RiotBot/riotbot
cp datestringdict.txt datestringdict.txt.backup
cp savedhashmap.txt savedhashmap.txt.backup
cp savedrolehashmap.txt savedrolehashmap.txt.backup
```

### View Disk Usage

```bash
# Check Docker disk usage
docker system df

# Clean up old images
docker system prune -a
```

## Advanced: Auto-Start on Boot

Docker Compose already has `restart: unless-stopped`, but to ensure Docker starts on boot:

```bash
sudo systemctl enable docker
```

## Security Best Practices

1. **Never commit .env file** - Already in .gitignore
2. **Use SSH keys, not passwords**
3. **Regularly update Pi**: `sudo apt update && sudo apt upgrade`
4. **Change default Pi password**: `passwd`
5. **Use fail2ban**: `sudo apt install fail2ban`
6. **Limit SSH key permissions**: `chmod 600 ~/.ssh/pi_deploy`

## Next Steps

Consider adding:
- Health checks in docker-compose.yml
- Discord notifications on deployment success/failure
- Staging environment for testing
- Automatic backups of data files
- Monitoring with Prometheus/Grafana