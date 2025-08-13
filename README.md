# Autonomous-Launch-Orchestrator

# 🚀 Autonomous Launch Orchestrator

An AI-driven multi-agent system that autonomously plans, coordinates, and executes product launch tasks using LLM reasoning and n8n workflow automation — with human approval for safety.

## 🎯 Problem it Solves

Launching a product requires **cross-functional coordination** — marketing campaigns, developer updates, legal compliance, customer outreach — often managed manually across tools. This leads to **missed deadlines, poor communication, and repetitive work**.

The Autonomous Launch Orchestrator solves this by:

* Planning the entire launch timeline from a **natural language goal**
* Assigning tasks to **specialized AI agents**
* Executing repetitive work through **n8n automations**
* Involving humans for approvals before high-impact actions

## 🏗️ Architecture

```
User Input → LLM Planner Agent → Task Database → Specialized Role Agents
                                      ↓
Human Approval System ← Monitoring Dashboard ← n8n Execution Layer
                                      ↓
                              External APIs (Twitter, GitHub, Mailchimp, etc.)
```

## 🛠️ Tech Stack

* **LLM Orchestration:** LangChain for agent coordination (Google Gemini)
* **Backend:** FastAPI for API endpoints and orchestration logic
* **Frontend:** Streamlit dashboard for task management
* **Automation Engine:** n8n for workflow automation
* **Database:** PostgreSQL for task states & execution logs
* **Infrastructure:** Docker Compose for deployment

## 🚀 Quick Start

### Prerequisites

* Docker and Docker Compose
* Google Gemini API key
* Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd autonomous_launch_orchestrator
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

This will start:
* **Backend API** on http://localhost:8000
* **Frontend Dashboard** on http://localhost:8501
* **n8n Workflow Engine** on http://localhost:5678
* **PostgreSQL Database** on localhost:5432

### 4. Access the Application

1. Open http://localhost:8501 for the main dashboard
2. Open http://localhost:5678 for n8n workflow management
3. API documentation available at http://localhost:8000/docs

## 📖 Usage Guide

### Creating a Launch Plan

1. Navigate to the **Create Plan** page
2. Enter your launch goal (e.g., "Launch our new AI chatbot in 3 weeks")
3. Click **Generate Plan**
4. The system will create structured tasks across different roles

### Managing Tasks

1. Go to **Task Management** page
2. Review generated tasks by role, status, and priority
3. **Approve** tasks to trigger automated execution
4. **Reject** tasks that need revision
5. Monitor execution status in real-time

### Monitoring Execution

1. Visit **Execution Logs** page
2. View detailed logs of all workflow executions
3. Track success/failure rates and execution details

## 🔧 Development Setup

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py

# Database (using Docker)
docker run -d \
  --name postgres \
  -e POSTGRES_DB=orchestrator_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:13

# n8n (using Docker)
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### API Endpoints

* `POST /api/create-plan` - Create launch plan from goal
* `GET /api/tasks` - Get all tasks
* `POST /api/tasks/{task_id}/approve` - Approve and execute task
* `POST /api/tasks/{task_id}/reject` - Reject task
* `GET /api/logs` - Get execution logs

## 🔌 n8n Workflows

The system includes pre-configured workflows for:

* **Social Media Posting** - Automated social media campaigns
* **Email Campaigns** - Marketing email automation
* **GitHub Updates** - Release notes and repository updates

### Adding Custom Workflows

1. Access n8n at http://localhost:5678
2. Import workflow JSON files from `n8n/workflows/`
3. Configure webhook URLs and API connections
4. Update workflow mapping in `backend/app/core/n8n_integration.py`

## 🎨 Customization

### Adding New Agent Roles

1. Update `RoleAgent` class in `backend/app/core/agents.py`
2. Add role-specific prompts and logic
3. Update workflow mapping in n8n integration

### Extending Workflows

1. Create new workflow JSON in `n8n/workflows/`
2. Add workflow mapping in `N8NIntegration` class
3. Test workflow execution through the dashboard

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
streamlit run app.py --server.headless true
```

## 📊 Example Use Case

**Input:** "Launch AI-powered finance tracker by Oct 10th"

**Generated Tasks:**
* **Marketing:** Social campaign, blog post, YouTube demo
* **Developer:** Push final release, update documentation
* **Legal:** Verify compliance for EU/US markets
* **Sales:** Email existing customers, update pricing page

**Automated Execution:**
* Social media posts scheduled and published
* Release notes generated and pushed to GitHub
* Email campaigns sent to customer segments
* Compliance documents reviewed and filed

## 🔒 Security & Safety

* **Human-in-the-loop approval** for all high-impact actions
* **Webhook validation** for n8n integrations
* **Environment variable protection** for API keys
* **Database isolation** with Docker networking

## 🚀 Deployment

### Production Deployment

1. Update environment variables for production
2. Configure external database (AWS RDS, etc.)
3. Set up reverse proxy (nginx) for HTTPS
4. Deploy using Docker Compose or Kubernetes

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Portfolio Impact

This project demonstrates:

* **Multi-agent LLM orchestration** with LangChain
* **Workflow automation** integration with n8n
* **Human-in-the-loop safety** controls
* **Full-stack development** with FastAPI and Streamlit
* **Containerized deployment** with Docker
* **Real-world business automation** use case

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the [Issues](https://github.com/your-repo/issues) page
2. Review the [Documentation](https://github.com/your-repo/wiki)
3. Contact the development team

---

**Built with ❤️ for autonomous business process automation**

