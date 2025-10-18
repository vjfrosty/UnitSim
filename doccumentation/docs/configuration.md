# FastMCP Server Deployment Configuration

Complete guide to deploying a FastMCP server with Docker, nginx, and HTTPS.

## System Information

- **OS**: Ubuntu Linux
- **Server**: nginx/1.24.0
- **Domain**: ai-contextengineering.com
- **SSL**: Let's Encrypt
- **Container Runtime**: Docker with Docker Compose

---

## 1. Prerequisites Installation

### Install Docker

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Install nginx

```bash
# Install nginx
sudo apt update
sudo apt install -y nginx

# Start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify installation
nginx -v
```

### Install Certbot (Let's Encrypt SSL)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d ai-contextengineering.com -d www.ai-contextengineering.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

## 2. Project Structure

```
/srv/pizza/
├── docker-compose.yml
└── app/
    ├── Dockerfile
    ├── requirements.txt
    ├── server.py
    └── assets/
        └── pizzaz.html
```

---

## 3. Project Files

### docker-compose.yml

```yaml
version: '3.8'
services:
  pizza-app:
    build: ./app
    container_name: mcp_pizza_app
    ports:
      - "127.0.0.1:8000:8000" 
    restart: unless-stopped

networks:
  mcpnet:
    driver: bridge
```

### app/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server module and assets into the image
COPY server.py .
COPY assets/ ./assets/

EXPOSE 8000

# Run FastMCP server directly
CMD ["python", "server.py"]
```

### app/requirements.txt

```txt
mcp[fastapi]>=0.1.0
fastapi>=0.115.0
fastmcp
pydantic
```

### app/server.py

```python
from fastmcp import FastMCP
from typing import Dict, List, Any
from pydantic import BaseModel, Field, ConfigDict, ValidationError
import mcp.types as types
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

# --- Widget / UI structures (optional) ---
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

@lru_cache(maxsize=None)
def _load_widget_html(name: str) -> str:
    path = ASSETS_DIR / f"{name}.html"
    if path.exists():
        return path.read_text(encoding="utf8")
    return ""  # fallback empty

class PizzazWidget:
    def __init__(self, identifier: str, title: str, template_uri: str,
                 invoking: str, invoked: str, html: str, response_text: str):
        self.identifier = identifier
        self.title = title
        self.template_uri = template_uri
        self.invoking = invoking
        self.invoked = invoked
        self.html = html
        self.response_text = response_text

widgets: List[PizzazWidget] = [
    PizzazWidget(
        identifier="pizza-map",
        title="Show Pizza Map",
        template_uri="ui://widget/pizza-map.html",
        invoking="Show map",
        invoked="Map shown",
        html=_load_widget_html("pizzaz"),
        response_text="Rendered a pizza map"
    )
]

WIDGETS_BY_ID = {w.identifier: w for w in widgets}
WIDGETS_BY_URI = {w.template_uri: w for w in widgets}

# --- Input schema class ---
class PizzaInput(BaseModel):
    pizza_topping: str = Field(..., alias="pizzaTopping")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

# --- Initialize MCP ---
mcp = FastMCP(name="pizzaz-minimal")

# --- Define tool using FastMCP decorator ---
@mcp.tool()
async def pizza_map(pizzaTopping: str) -> str:
    """Show a pizza map with the specified topping"""
    widget = WIDGETS_BY_ID.get("pizza-map")
    if widget:
        return f"Pizza with {pizzaTopping} ordered! {widget.response_text}"
    return f"Pizza with {pizzaTopping} ordered!"

# For uvicorn, create app entry point
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

### app/assets/pizzaz.html

```html
<div style="padding: 20px; border: 2px solid #ff6b6b; border-radius: 8px;">
    <h2>🍕 Pizza Map</h2>
    <p>Your pizza is being prepared!</p>
</div>
```

---

## 4. nginx Configuration

### /etc/nginx/sites-enabled/ai-contextengineering.com

```nginx
server {
    server_name ai-contextengineering.com www.ai-contextengineering.com;

    root /var/www/ai-contextengineering.com/html;
    index index.html index.htm;

    # Serve components UI
    location /components/ {
        try_files $uri $uri/ /components/index.html;
    }

    # Proxy MCP streamable-http endpoint
    location /mcp {
        proxy_pass http://127.0.0.1:8000/mcp;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header Content-Type $http_content_type;
        proxy_set_header Accept $http_accept;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Proxy messages endpoint
    location ~ ^/messages {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        
        proxy_buffering off;
        proxy_cache off;
    }

    # Static / root fallback
    location / {
        try_files $uri $uri/ =404;
    }

    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    ssl_certificate /etc/letsencrypt/live/ai-contextengineering.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai-contextengineering.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    listen [::]:80;
    server_name ai-contextengineering.com www.ai-contextengineering.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}
```

---

## 5. MCP Manifest for OpenAI

### /var/www/ai-contextengineering.com/html/.well-known/mcp.json

```json
{
  "mcpServers": {
    "pizzaz-minimal": {
      "url": "https://ai-contextengineering.com/mcp"
    }
  }
}
```

---

## 6. Deployment Commands

### Initial Setup

```bash
# Create project directory
sudo mkdir -p /srv/pizza/app/assets

# Create all project files (see section 3)
# Copy files to /srv/pizza/

# Set permissions
sudo chown -R $USER:$USER /srv/pizza

# Create nginx config
sudo nano /etc/nginx/sites-available/ai-contextengineering.com

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-contextengineering.com /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Create MCP manifest directory
sudo mkdir -p /var/www/ai-contextengineering.com/html/.well-known

# Create manifest file
sudo nano /var/www/ai-contextengineering.com/html/.well-known/mcp.json
```

### Build and Run

```bash
# Navigate to project directory
cd /srv/pizza

# Build and start containers
docker compose up -d --build

# View logs
docker logs -f mcp_pizza_app

# Verify container is running
docker ps | grep mcp_pizza_app
```

---

## 7. Testing

### Test Direct Container Access

```bash
# Test initialize endpoint
curl -N -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'
```

### Test Through nginx

```bash
# Test initialize through HTTPS
curl -N -X POST https://ai-contextengineering.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'

# Test manifest
curl https://ai-contextengineering.com/.well-known/mcp.json
```

---

## 8. Maintenance Commands

### View Logs

```bash
# Container logs
docker logs mcp_pizza_app

# Follow logs
docker logs -f mcp_pizza_app

# nginx error logs
sudo tail -f /var/log/nginx/error.log

# nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### Restart Services

```bash
# Restart container
cd /srv/pizza
docker compose restart

# Rebuild and restart
docker compose down
docker compose up -d --build

# Restart nginx
sudo systemctl restart nginx

# Reload nginx (no downtime)
sudo systemctl reload nginx
```

### Update Application

```bash
# Navigate to project
cd /srv/pizza

# Stop containers
docker compose down

# Update code (edit files)

# Rebuild with no cache
docker compose build --no-cache

# Start containers
docker compose up -d

# Verify
docker logs -f mcp_pizza_app
```

---

## 9. Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs mcp_pizza_app

# Check container status
docker ps -a | grep mcp_pizza_app

# Rebuild from scratch
cd /srv/pizza
docker compose down
docker compose build --no-cache
docker compose up -d
```

### nginx 502 Bad Gateway

```bash
# Check container is running
docker ps | grep mcp_pizza_app

# Check container is listening on correct port
docker exec mcp_pizza_app netstat -tlnp | grep 8000

# Test direct connection
curl http://127.0.0.1:8000/mcp

# Check nginx error logs
sudo tail -50 /var/log/nginx/error.log
```

### SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate expiration
sudo certbot certificates
```

---

## 10. Key Configuration Points

### FastMCP Transport

- **Transport**: `streamable-http` (supports both SSE and JSON-RPC over HTTP)
- **Host**: `0.0.0.0` (listen on all interfaces inside container)
- **Port**: `8000` (mapped to host 127.0.0.1:8000)

### nginx Proxy

- **Critical**: Forward both `Content-Type` and `Accept` headers
- **Buffering**: Must be disabled for streaming responses
- **Timeouts**: Set to 86400s (24 hours) for long-lived connections
- **Path**: `/mcp` proxies to `http://127.0.0.1:8000/mcp`

### Docker Networking

- Container binds to `127.0.0.1:8000` on host (not exposed publicly)
- nginx reverse proxy provides HTTPS termination
- Only nginx (port 443) is exposed to the internet

---

## 11. Security Considerations

1. **Container isolation**: Container only accessible via localhost
2. **HTTPS only**: All external traffic uses SSL/TLS
3. **nginx as gateway**: Single point of control for external access
4. **No direct container exposure**: Port 8000 only bound to 127.0.0.1
5. **Automatic SSL renewal**: Certbot handles certificate updates

---

## 12. Adding to OpenAI ChatGPT

1. Navigate to ChatGPT settings
2. Add MCP server: `https://ai-contextengineering.com`
3. ChatGPT will discover the server via `/.well-known/mcp.json`
4. Tools will be available in chat interface

### Required Headers for MCP Clients

```
Content-Type: application/json
Accept: application/json, text/event-stream
```

---

## Reproduction Checklist

- [ ] Install Docker and Docker Compose
- [ ] Install nginx
- [ ] Obtain SSL certificate with Certbot
- [ ] Create project structure in `/srv/pizza`
- [ ] Create all project files (Dockerfile, docker-compose.yml, server.py, etc.)
- [ ] Create nginx configuration in `/etc/nginx/sites-available/`
- [ ] Enable nginx site
- [ ] Create MCP manifest in `.well-known/mcp.json`
- [ ] Build and start Docker containers
- [ ] Test endpoints
- [ ] Add to OpenAI ChatGPT

---

**Documentation created**: October 17, 2025  
**Server**: ai-contextengineering.com  
**Framework**: FastMCP 2.12.4  
**MCP SDK**: 1.18.0
