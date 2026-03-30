# 🚀 Cybabot Ultra - Production Deployment Guide

This guide covers everything you need to deploy Cybabot Ultra to production.

## 📋 Prerequisites

Before deploying, you need:

### 1. API Keys Setup

Create accounts and get API keys from:

- **LLM Providers** (choose at least one):
  - [Groq](https://console.groq.com/) - Free tier available
  - [Anthropic Claude](https://anthropic.com/) - API access
  - [DeepSeek](https://platform.deepseek.com/) - API access  
  - [Google Gemini](https://aistudio.google.com/) - API access
  - [Ollama](https://ollama.ai/) - Local models (free)

- **Payment Processing**:
  - [Stripe](https://stripe.com/) - Payment gateway
    - Get Publishable Key, Secret Key, Webhook Secret

- **Database** (if using cloud):
  - [Neon](https://neon.tech/) - Serverless PostgreSQL (free tier)
  - [Supabase](https://supabase.com/) - PostgreSQL + auth
  - [Railway](https://railway.app/) - PostgreSQL plugin

- **Domain & SSL**:
  - [Cloudflare](https://cloudflare.com/) - Domain + CDN + SSL
  - Or use platform-provided domains (usually *.railway.app, *.vercel.app, etc.)

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys:

```env
# Database
DATABASE_URL="postgresql://user:password@host:5432/cybabot"

# JWT Authentication
JWT_SECRET_KEY="your-super-secret-jwt-key-here"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Payments
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_PUBLISHABLE_KEY="pk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRICE_STARTER="price_..."
STRIPE_PRICE_PROFESSIONAL="price_..."
STRIPE_PRICE_ENTERPRISE="price_..."

# LLM Providers (at least one required)
GROQ_API_KEY="gsk_..."
ANTHROPIC_API_KEY="sk-ant-..."
DEEPSEEK_API_KEY="sk-..."
GEMINI_API_KEY="..."

# Optional: Ollama (local models)
OLLAMA_BASE_URL="http://localhost:11434"

# Frontend URL (for CORS and Stripe callbacks)
FRONTEND_URL="https://yourdomain.com"
```

---

## 🏗️ Deployment Options

### Option 1: Railway (Recommended - Easiest)

Railway offers the fastest path to production with minimal configuration.

#### Backend Deployment

1. **Create Railway Account**
   ```
   Visit: https://railway.app
   Sign up with GitHub
   ```

2. **Deploy Backend**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   cd backend
   railway init
   
   # Deploy
   railway up
   ```

3. **Add Environment Variables**
   - Go to Railway Dashboard → Your Project → Variables
   - Add all variables from `.env`
   - Add `PYTHON_VERSION=3.11`

4. **Configure Startup Command**
   - Railway Dashboard → Your Project → Settings
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Database Setup

1. **Create PostgreSQL Database**
   ```bash
   railway add postgresql
   ```

2. **Run Migrations**
   ```bash
   cd prisma
   DATABASE_URL="postgresql://..." railway run npx prisma migrate deploy
   ```

#### Frontend Deployment

1. **Deploy to Vercel** (recommended) or Railway
   
   **Vercel** (recommended for Next.js):
   ```bash
   cd frontend
   npm install -g vercel
   vercel
   ```
   
   **Railway**:
   ```bash
   cd frontend
   railway init
   railway up
   ```

2. **Configure Environment Variables**
   - Set `NEXT_PUBLIC_API_URL` to your backend URL
   - Set `NEXT_PUBLIC_APP_URL` to your frontend URL

---

### Option 2: Docker + VPS/Cloud

Best for full control and custom infrastructure.

#### 1. Server Setup

Choose a cloud provider:
- **DigitalOcean** ($4-6/month) - Simple VPS
- **AWS EC2** - Free tier available
- **Linode** - Affordable VPS
- **Hetzner** - Best price/performance

#### 2. Install Docker

```bash
# SSH into your server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose

# Add user to docker group
usermod -aG docker $USER
```

#### 3. Configure Production Files

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      # ... other env vars
    restart: always
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    restart: always
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    restart: always
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres_data:
```

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name yourdomain.com;
        
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

#### 4. Deploy

```bash
# SSH into server
ssh root@your-server-ip

# Clone repository
git clone https://github.com/yourusername/cybabot.git
cd cybabot

# Create production .env
nano .env  # Paste your environment variables

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python -m prisma migrate deploy
```

#### 5. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
apt install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

---

### Option 3: Kubernetes (Advanced)

For container orchestration and scaling.

#### Helm Chart Structure

Create `charts/cybabot/values.yaml`:

```yaml
replicaCount: 2

image:
  backend: yourregistry/cybabot-backend:latest
  frontend: yourregistry/cybabot-frontend:latest

service:
  type: LoadBalancer
  ports:
    frontend: 3000
    backend: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: yourdomain.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

postgresql:
  enabled: true
  auth:
    database: cybabot
    username: cybabot
    password: your-secure-password

secrets:
  # Use external secrets or vault
  DATABASE_URL: "postgresql://..."
  JWT_SECRET_KEY: "..."
  STRIPE_SECRET_KEY: "..."
```

#### Deploy

```bash
# Install kubectl and helm
# Configure kubeconfig

# Add repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Deploy
helm install cybabot ./charts/cybabot -n cybabot --create-namespace

# Check status
kubectl get pods -n cybabot
kubectl get services -n cybabot
```

---

## 🔒 Security Checklist

Before going live:

- [ ] **HTTPS/SSL** - All traffic encrypted
- [ ] **JWT Secret** - Strong, random 64+ character key
- [ ] **Stripe Webhooks** - Verify webhook signatures
- [ ] **CORS** - Configure allowed origins
- [ ] **Rate Limiting** - Enable on API endpoints
- [ ] **Database** - Strong credentials, SSL connections
- [ ] **Environment Variables** - No secrets in code
- [ ] **Dependencies** - Regular security updates
- [ ] **Backups** - Database backups configured
- [ ] **Monitoring** - Logging and alerting setup

---

## 💳 Stripe Setup

### 1. Create Products & Prices

```bash
# Using Stripe CLI (recommended)
stripe products create \
  --name="Cybabot Starter" \
  --description="100 credits" \
  --unit-amount=999

# Note the price ID, repeat for other tiers
```

### 2. Configure Webhooks

```bash
# Install Stripe CLI
stripe listen --forward-to localhost:8000/api/webhooks/stripe

# In production:
stripe listen --forward-to yourdomain.com/api/webhooks/stripe
```

### 3. Update Environment Variables

Add Stripe Price IDs to `.env`:
```env
STRIPE_PRICE_STARTER="price_xxxxxxxxxxxx"
STRIPE_PRICE_PROFESSIONAL="price_xxxxxxxxxxxx"
STRIPE_PRICE_ENTERPRISE="price_xxxxxxxxxxxx"
```

---

## 🧪 Testing Deployment

### 1. Smoke Tests

```bash
# Test backend health
curl https://yourbackend.com/health

# Test frontend
curl https://yourdomain.com

# Test WebSocket
wscat -c wss://yourbackend.com/ws/test
```

### 2. Stripe Test Mode

- Use Stripe test mode keys during development
- Test cards: https://stripe.com/docs/testing
- Test webhook events in dashboard

### 3. Load Testing

```bash
# Install artillery
npm install -g artillery

# Run test
artillery quick --count 100 -n 20 https://yourdomain.com/api/health
```

---

## 📊 Monitoring & Logging

### Backend Logs

```bash
# View logs (Docker)
docker-compose logs -f backend

# View logs (Railway)
railway logs -f

# Application logs
tail -f logs/app.log
```

### Set up Monitoring

```bash
# Use Sentry for error tracking
pip install sentry-sdk

# In your Python code
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

### Health Checks

Your backend already includes health checks at `/health`. Configure uptime monitoring:

- [UptimeRobot](https://uptimerobot.com/) - Free tier
- [Better Uptime](https://betteruptime.com/) - Free tier
- [Pingdom](https://pingdom.com/) - Trial available

---

## 🚀 CI/CD Pipeline

Your GitHub Actions pipeline is already configured in `.github/workflows/ci.yml`.

### Setup

1. **Add GitHub Secrets**
   ```bash
   Go to: GitHub → Settings → Secrets and variables → Actions
   
   Add:
   - RAILWAY_TOKEN (if using Railway)
   - VERCEL_TOKEN (if using Vercel)
   - DATABASE_URL (for migrations)
   ```

2. **Enable GitHub Actions**
   - Push to `main` branch will trigger deployment
   - PRs will run tests automatically

### Custom Deployment

Modify `.github/workflows/deploy.yml`:

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    # Add your deployment steps here
    # Example: Railway
    - name: Deploy to Railway
      run: |
        npm install -g @railway/cli
        railway login --token ${{ secrets.RAILWAY_TOKEN }}
        railway up --service backend
    
    # Example: Docker
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        script: |
          cd /app/cybabot
          git pull
          docker-compose -f docker-compose.prod.yml up -d
```

---

## 🌐 Domain Configuration

### DNS Setup (Cloudflare)

1. **Add DNS Records**
   ```
   Type    Name    Content              Proxy
   A       @       YOUR_SERVER_IP       Proxied
   CNAME   www     yourdomain.com        Proxied
   CNAME   api     yourbackend.com       Proxied
   ```

2. **SSL/TLS Settings**
   - Mode: Full (Strict)
   - TLS 1.2 minimum
   - Enable "Always Use HTTPS"

### Subdomains

```nginx
# nginx.conf
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://backend:8000;
        # ... other proxy settings
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://frontend:3000;
        # ... other proxy settings
    }
}
```

---

## 🔄 Updates & Maintenance

### Updating Code

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
# Docker
docker-compose -f docker-compose.prod.yml up -d --build

# Railway
railway up

# Vercel
vercel --prod
```

### Database Migrations

```bash
# Apply new migrations
npx prisma migrate deploy

# Or create new migration
npx prisma migrate dev --name add_new_feature
```

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U postgres -h localhost cybabot > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres -h localhost cybabot < backup_20240101.sql
```

---

## 💰 Cost Estimation

### Starter Tier ($0-15/month)

- Railway Hobby: Free
- Neon Free Tier: Free
- Domain: $10-15/year
- **Total: ~$1/month**

### Professional Tier ($50-100/month)

- Railway Pro: $20/month
- Neon Pay-as-you-go: $10-30/month
- Domain + SSL: $15/year
- **Total: ~$50-70/month**

### Enterprise Tier ($200+/month)

- Railway Pro: $100/month
- Managed Database: $50-100/month
- CDN + Extra resources: $50+/month
- **Total: ~$200-300/month**

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check DATABASE_URL format
postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL

# Check if PostgreSQL is running
docker-compose logs db
```

**CORS Errors**
```python
# In backend/app/main.py, ensure CORS is configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
)
```

**Stripe Webhooks Not Working**
```bash
# Check webhook logs
stripe logs list

# Verify webhook signature
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

**Frontend 502 Bad Gateway**
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs nginx
docker-compose logs frontend
```

**Build Failures**
```bash
# Clear caches
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose -f docker-compose.prod.yml build --no-cache
```

---

## 📞 Support

For deployment help:
1. Check [Railway Docs](https://docs.railway.app/)
2. Check [Vercel Docs](https://vercel.com/docs)
3. Check [Docker Docs](https://docs.docker.com/)
4. Check [Nginx Docs](https://nginx.org/en/docs/)

For Cybabot issues:
- Check `plans/ARCHITECTURE.md` for system design
- Check backend logs for API errors
- Check browser console for frontend errors

---

## ✅ Deployment Checklist

Before going live:

- [ ] All API keys configured
- [ ] Database migrations run
- [ ] HTTPS/SSL enabled
- [ ] Stripe webhook configured
- [ ] Health checks passing
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Error tracking enabled
- [ ] DNS configured
- [ ] Domain SSL valid
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Security scan complete
- [ ] Load tested
- [ ] Documentation complete

**🎉 Congratulations! Your Cybabot Ultra is now live!**