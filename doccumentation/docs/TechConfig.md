Got it — here’s a tight record of the **configs that actually worked**, exactly as we verified on your box.

# ✅ Working configuration snapshot

## Domains, paths, listeners

* **Domain:** `ai-contextengineering.com` (TLS/HTTP2 via NGINX)
* **Webroot (HTTPS vhost):** `/var/www/ai-contextengineering.com/html/`
* **Static components path:** `/var/www/ai-contextengineering.com/html/components/`
* **App (Uvicorn/FastAPI) bind:** `127.0.0.1:8000` (loopback only)
* **Public endpoints:**

  * `https://ai-contextengineering.com/mcp/manifest`
  * `https://ai-contextengineering.com/mcp/call`
  * `https://ai-contextengineering.com/components/index.html`
  * (Artifacts served under) `https://ai-contextengineering.com/components/demo-artifacts/`

---

## NGINX (inside the TLS :443 server block)

```nginx
# Serve static components from the real webroot
location /components/ {
    try_files $uri $uri/ /components/index.html;
    add_header Cache-Control "public, max-age=300";
}

# Reverse proxy to the MCP server (Uvicorn on loopback)
location /mcp/ {
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 300;
    proxy_send_timeout 300;

    # IMPORTANT: trailing /mcp/ in both location and proxy_pass
    proxy_pass http://127.0.0.1:8000/mcp/;
}
```

**Notes that fixed issues:**

* Using the **correct webroot** with `/html/`.
* Matching **trailing slashes** in `location /mcp/` and `proxy_pass .../mcp/`.
* After changes: `sudo nginx -t && sudo systemctl reload nginx`.

---

## Docker / Compose layout

**Project home:** `/srv/docrefine/`

```
/srv/docrefine/
  docker-compose.yml
  app/
    Dockerfile
    requirements.txt
    server.py
  components/
    Dockerfile
    package.json
    src/
      index.js
      static/index.html
```

### docker-compose.yml (effective bits)

```yaml
services:
  app:
    build: ./app
    image: docrefine-app:0.1.0
    container_name: docrefine-app
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"   # loopback only
    networks: [docrefine]

  components:
    build: ./components
    image: docrefine-components:0.1.0
    container_name: docrefine-components
    restart: unless-stopped
    # used to produce static build; not exposed publicly
    ports:
      - "127.0.0.1:8080:80"
    networks: [docrefine]

networks:
  docrefine:
    driver: bridge
```

---

## FastAPI MCP server (confirmed live)

* **`GET /mcp/manifest`** → JSON manifest with **3 tools** (`parse`, `apply_style`, `export`) and `components_base_url`.
* **`POST /mcp/call`** → accepts `{"tool":"...", "arguments":{...}}`.

**App container:** `docrefine-app` (Python 3.11-slim, FastAPI, Uvicorn, Pydantic).

---

## Components build & deployment (that worked)

**Dockerfile (lockfile optional):**

```Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY src ./src
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
```

**Post-build copy to webroot:**

```bash
docker compose build components
docker compose up -d components

docker cp docrefine-components:/usr/share/nginx/html /tmp/docrefine-components
sudo mkdir -p /var/www/ai-contextengineering.com/html/components
sudo rsync -av /tmp/docrefine-components/ /var/www/ai-contextengineering.com/html/components/

sudo chown -R www-data:www-data /var/www/ai-contextengineering.com/html/components
sudo find /var/www/ai-contextengineering.com/html/components -type d -exec chmod 755 {} \;
sudo find /var/www/ai-contextengineering.com/html/components -type f -exec chmod 644 {} \;
```

**Result:** `https://ai-contextengineering.com/components/index.html` returns 200.

---

## Sanity checks (used and passed)

```bash
# Manifest JSON (HTTPS through NGINX)
curl -s https://ai-contextengineering.com/mcp/manifest | python3 -m json.tool | head

# Call endpoint error path (proves dispatch + JSON handling)
curl -sD - https://ai-contextengineering.com/mcp/call \
  -H 'Content-Type: application/json' \
  -d '{"tool":"__unknown__","arguments":{}}' | head

# Local app (bypass NGINX) if needed
curl -s http://127.0.0.1:8000/mcp/manifest | python3 -m json.tool | head

# Logs while testing
docker logs -f docrefine-app
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

---

## Tech stack (as deployed)

* **OS / Security:** Ubuntu LTS, UFW, Fail2ban (assumed hardened SSH)
* **Reverse proxy / TLS:** NGINX (HTTP/2, Let’s Encrypt certs already in place)
* **Containers:** Docker Engine + docker compose plugin
* **Backend app:** Python 3.11-slim, **FastAPI 0.115**, **Uvicorn 0.30**, **Pydantic 2.8**
* **Frontend components:** Node 20 (alpine) + **esbuild** → static HTML/JS
* **Networking:** Public ports only on NGINX; app on 127.0.0.1:8000
* **Static hosting:** `/var/www/ai-contextengineering.com/html/components/` via NGINX

---


