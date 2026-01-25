---
title: "Install"
slug: "install"
toc:
    enabled: true
    floating: true
visible: true
---

![Gravity](gravit.jpg?width=550)

! This document will guide you through the complete process of deploying the CMS on a Linux server (e.g., Debian/Ubuntu) from scratch to a functional website running under your own domain.

## 1. Prerequisites

Before you begin, ensure that you have the following tools installed on your server:
- `git`
- `python3` and `python3-venv`
- `nginx`
- `certbot` (recommended for SSL)

You can install them easily using the package manager:
```bash
apt update
apt install git python3 python3-venv nginx
```

## 2. Environment Preparation

It is recommended to run the application under an unprivileged user, such as `www-data`.

#### Step 1: Clone the Repository
Clone or copy the project into the target directory. We will use `/var/www/DOMAIN` as an example.

```bash
# Create the directory for the project:
mkdir -p /var/www/DOMAIN
mkdir -p /var/www/DOMAIN/run

# Clone the project:
git clone <REPOZITORY> /var/www/DOMAIN

# Set the correct permissions:
chown www-data:www-data -R /var/www/DOMAIN
```

#### Step 2: Create a Virtual Environment
The application will run in an isolated Python environment.

```bash
# Switch to the project directory
cd /var/www/DOMAIN

# Create the venv (as the www-data user)
sudo -u www-data python3 -m venv venv
```

#### Step 3: Install Dependencies
Install all necessary Python libraries.

```bash
# Run pip from our venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt
```

## 3. Systemd Configuration

For reliable background operation, we will use `systemd` with socket-based activation. `systemd` will listen on a socket and start the application only upon the first incoming request. We will use Uvicorn as the Python wrapper.

#### Step 1: Create the Socket File
Create the file `/etc/systemd/system/uvicorn-DOMAIN.socket`:
```
# /etc/systemd/system/uvicorn-DOMAIN.socket
[Unit]
Description=Uvicorn socket for CMS

[Socket]
ListenStream=/var/www/DOMAIN/run/uvicorn-DOMAIN.sock
SocketUser=www-data
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

!!! Ensure that the directory `/var/www/DOMAIN/run/` exists and has the correct permissions so that the `www-data` user can write to it.

#### Step 2: Create the Service File
Create the file `/etc/systemd/system/uvicorn-DOMAIN.service`:
```
# /etc/systemd/system/uvicorn-DOMAIN.service
[Unit]
Description=Uvicorn service for CMS
Requires=uvicorn-DOMAIN.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/DOMAIN
Environment="PYTHONPATH=/var/www/DOMAIN/venv/lib/python3.11/site-packages"
ExecStart=/var/www/DOMAIN/venv/bin/uvicorn main:app --workers 3 --uds /var/www/DOMAIN/run/uvicorn-DOMAIN.sock --proxy-headers
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

!! Do not forget to adjust the path in `PYTHONPATH` according to your Python version (e.g., `python3.11`, `python3.13`, etc.).

#### Step 3: Start and Enable Services
```bash
# Reload the systemd configuration
systemctl daemon-reload

# Enable and immediately start the socket
systemctl enable --now uvicorn-DOMAIN.socket

# Verify that the socket is listening
systemctl status uvicorn-DOMAIN.socket
```

## 4. Nginx Configuration

Nginx will serve as a reverse proxy—it will accept requests from the internet and forward them to our application running on the socket. It will also handle the efficient serving of static files (CSS, JS, images).

Create the file `/etc/nginx/sites-available/DOMAIN.conf` (replace DOMAIN with your domain):

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name DOMAIN;
    root /var/www/DOMAIN;

    location ^~ /.well-known/acme-challenge/ {
       alias /var/www/DOMAIN/.well-known/acme-challenge/;
    }

    # Redirect to HTTPS and handler for Certbot
    location / {
        return 302 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;

    http2 on; 

    access_log      /var/log/nginx/DOMAIN-access.log;
    error_log       /var/log/nginx/DOMAIN-error.log;

    server_name DOMAIN;
    root /var/www/DOMAIN/;

    # Paths to SSL certificates (obtained via Certbot)
    ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;		# Certificates must be created beforehand using Certbot or another Acme client
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN/privkey.pem;

    # Security: Deny direct access to content and accounts
    location ~* ^/(user)/pages/.*\.(jpg|jpeg|gif|png|webp|bmp)$ {
        expires 7d;
        access_log off;
    }

    location ~* ^/user/(accounts|pages|accounts|plugin)/.*\.(md|yaml|yml|txt)$ {
        deny all;
    }

    location = /favicon.svg {
        access_log off;
        log_not_found off;
        expires 7d;
    }

    location = /user/plugin/optimizer/service-worker.js {
        add_header 'Service-Worker-Allowed' '/';
        add_header 'Cache-Control' 'no-cache, no-store, must-revalidate';
    }

    # Forward all other requests to our application
    location / {
        proxy_pass http://unix:/var/www/DOMAIN/run/uvicorn-DOMAIN.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Finalize Nginx Setup
```bash
# Activate the new configuration
ln -s /etc/nginx/sites-available/DOMAIN.conf /etc/nginx/sites-enabled/

# Test the syntax
nginx -t

# If all is well, restart Nginx
systemctl restart nginx
```

!! We recommend running `certbot --nginx` for the first time to automatically obtain and set up SSL certificates.

## 5. Final Check

If you have followed the steps correctly, your CMS should now be accessible on your domain.

You can monitor any application errors using:
```bash
journalctl -u uvicorn-DOMAIN.service -f
```
