# 🚀 Deployment Guide

## Quick Start (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key / Google Gemeni
- 4GB+ RAM available

### 1. Environment Setup
```bash
# Clone the project
git clone <your-repo-url>
cd autonomous_launch_orchestrator

# Copy and configure environment
cp .env .env.local
# Edit .env.local and add your OpenAI API key:
# OPENAI_API_KEY=your_actual_api_key_here
```

### 2. Start All Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access Applications
- **Main Dashboard**: http://localhost:8501
- **n8n Workflows**: http://localhost:5678
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Import n8n Workflows
1. Open http://localhost:5678
2. Go to "Workflows" → "Import from File"
3. Import each workflow from `n8n/workflows/`:
   - `social_media_post.json`
   - `email_campaign.json`
   - `github_update.json`

## Manual Setup (Development)

### Backend
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/orchestrator_db"
export OPENAI_API_KEY="your_api_key"

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt

# Start frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Database
```bash
# Start PostgreSQL with Docker
docker run -d \
  --name postgres \
  -e POSTGRES_DB=orchestrator_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:13
```

### n8n
```bash
# Start n8n with Docker
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

## Production Deployment

### Docker Compose Production
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```bash
# .env.prod
OPENAI_API_KEY=your_production_api_key
DATABASE_URL=postgresql://user:password@your-db-host:5432/orchestrator_db
N8N_BASE_URL=https://your-n8n-domain.com
ENVIRONMENT=production
```

### Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /n8n {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Cloud Deployment Options

### AWS
- **ECS**: Use docker-compose with ECS
- **RDS**: PostgreSQL managed database
- **ALB**: Application Load Balancer for routing

### Google Cloud
- **Cloud Run**: Containerized services
- **Cloud SQL**: PostgreSQL managed database
- **Cloud Load Balancing**: Traffic distribution

### Azure
- **Container Instances**: Docker containers
- **Azure Database**: PostgreSQL service
- **Application Gateway**: Load balancing

## Monitoring & Logging

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:8501/health
curl http://localhost:5678/healthz
```

### Logs
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f n8n
```

### Metrics (Optional)
Add Prometheus and Grafana for monitoring:
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

## Troubleshooting

### Common Issues

1. **Backend won't start**
   ```bash
   # Check database connection
   docker-compose logs postgres
   # Verify environment variables
   docker-compose exec backend env | grep DATABASE_URL
   ```

2. **Frontend can't connect to backend**
   ```bash
   # Check backend health
   curl http://localhost:8000/health
   # Verify CORS settings in backend
   ```

3. **n8n workflows not triggering**
   ```bash
   # Check n8n logs
   docker-compose logs n8n
   # Verify webhook URLs in workflows
   ```

4. **Database connection errors**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres
   # Wait for postgres to be ready, then start other services
   ```

### Performance Optimization

1. **Database**
   - Add indexes for frequently queried fields
   - Use connection pooling
   - Regular maintenance and backups

2. **Backend**
   - Enable caching for LLM responses
   - Use async operations where possible
   - Monitor API rate limits

3. **Frontend**
   - Implement pagination for large task lists
   - Add caching for static content
   - Optimize Streamlit performance

## Security Considerations

1. **API Keys**
   - Store in environment variables
   - Use secrets management in production
   - Rotate keys regularly

2. **Database**
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates

3. **Network**
   - Use HTTPS in production
   - Implement rate limiting
   - Monitor for suspicious activity

## Backup & Recovery

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U user orchestrator_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U user orchestrator_db < backup.sql
```

### Configuration Backup
```bash
# Backup n8n workflows
docker-compose exec n8n cp -r /home/node/.n8n/workflows ./n8n_backup/

# Backup environment files
cp .env .env.backup
```

## Scaling

### Horizontal Scaling
- Use load balancer for multiple backend instances
- Implement session management for frontend
- Use external database cluster

### Vertical Scaling
- Increase container resources
- Optimize database configuration
- Monitor resource usage

---

For additional support, check the main README.md or create an issue in the repository.

