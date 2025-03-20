# Bin Packing App Deployment Guide

Follow these steps to deploy the Bin Packing application on your VPS as a subdomain of dtanderson.net.

## Prerequisites
- Docker and Docker Compose installed on your VPS
- Nginx web server installed and configured
- Domain name (dtanderson.net) with DNS access

## Deployment Steps

### 1. Set up the Subdomain DNS

Add an A record for `binpacking.dtanderson.net` pointing to your VPS IP address.

```
Type: A
Name: binpacking
Value: <Your VPS IP address>
TTL: 3600 (or as preferred)
```

### 2. Transfer Files to VPS

Transfer your application files to your VPS:

```bash
# From your local machine
scp -r /path/to/bin-packing-app/* user@your-vps-ip:/path/to/bin-packing/
```

### 3. Set up Docker Network

Create a Docker network for your web services if it doesn't exist already:

```bash
ssh user@your-vps-ip
cd /path/to/bin-packing/
docker network create web
```

### 4. Configure Nginx

Copy the provided Nginx configuration file to the Nginx sites directory:

```bash
sudo cp nginx-config.conf /etc/nginx/sites-available/binpacking.dtanderson.net
sudo ln -s /etc/nginx/sites-available/binpacking.dtanderson.net /etc/nginx/sites-enabled/
```

### 5. Set up SSL with Let's Encrypt

Install Certbot and obtain SSL certificates:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d binpacking.dtanderson.net
```

### 6. Create a Data Directory

Create a directory for persistent data:

```bash
mkdir -p /path/to/bin-packing/data
chmod 777 /path/to/bin-packing/data
```

### 7. Start the Application

Deploy the application with Docker Compose:

```bash
cd /path/to/bin-packing/
docker-compose up -d
```

### 8. Test the Deployment

Verify the application is running:

```bash
docker-compose ps
docker logs bin-packing
```

Visit `https://binpacking.dtanderson.net` in your browser to confirm the application is working.

### 9. Set up Automatic Updates (Optional)

To keep the containers updated automatically, you can set up a cron job:

```bash
crontab -e
```

Add the following line to update the container weekly:

```
0 3 * * 0 cd /path/to/bin-packing/ && docker-compose pull && docker-compose up -d
```

## Maintenance Commands

### Restart the application
```bash
cd /path/to/bin-packing/
docker-compose restart
```

### View logs
```bash
docker-compose logs -f
```

### Stop the application
```bash
docker-compose down
```

### Update the application
```bash
git pull
docker-compose up -d --build
``` 