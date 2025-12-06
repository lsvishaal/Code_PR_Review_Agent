# CodeReview Agent 🤖

> **Automated GitHub PR Review Agent with Multi-Agent LLM System**

A production-grade FastAPI application that automatically reviews GitHub Pull Requests using specialized AI agents for logic analysis, readability, performance, and security.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![UV](https://img.shields.io/badge/UV-package%20manager-orange.svg)](https://github.com/astral-sh/uv)

---

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for different review aspects
  - Logic Agent: Detects logical flaws and edge cases
  - Readability Agent: Improves code clarity and maintainability
  - Performance Agent: Identifies optimization opportunities
  - Security Agent: Catches security vulnerabilities

- **Production-Ready**
  - Structured JSON logging with context
  - Prometheus metrics integration
  - Docker containerization with multi-stage builds
  - Comprehensive error handling
  - Type-safe with Pydantic models

- **GitHub Integration**
  - Fetch PRs directly from GitHub API
  - Parse diffs into structured format
  - Retrieve files, commits, and patch metadata per PR
  - Support for manual diff input and local CLI workflows

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Layer                       │
│                    (HTTP Endpoints)                     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼──────────┐
         │   Agent Manager      │
         │   (Orchestrator)     │
         └───────────┬──────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌─────▼─────┐
│  Logic    │  │ Reading │  │Performance│
│  Agent    │  │ Agent   │  │  Agent    │
└───────────┘  └─────────┘  └───────────┘
```

### Layer Separation (SoC)

```
src/
└── app/
    ├── api/          # HTTP endpoints (thin layer)
    ├── agents/       # Agent logic (core reasoning)
    ├── github/       # GitHub API client
    ├── diff/         # Diff parser
    ├── core/         # Config & logging
    └── models/       # Pydantic models
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (for local development)
- **UV package manager** (modern Python packaging tool)
- **Docker & Docker Compose** (recommended for full deployment)
- **GitHub Personal Access Token** (optional for public repos, required for private)
- **Ollama** (runs locally in Docker, no external API keys needed)

> **Note:** This system uses **Ollama** (local LLM) instead of cloud APIs like OpenAI. All inference happens on your machine - no data leaves your network.

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd code-review-agent
```

2. **Install UV** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Create virtual environment and install dependencies**
```bash
uv sync
```

4. **Create .env file from template**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run the application**
```bash
uv run uvicorn src.app.main:app --reload
```

The API will be available at `http://localhost:8000`

---

## � GitHub CLI Utilities

Use the helper script in `scripts/github_tools.py` to explore repository metadata and diff content without starting the API server.

```bash
# List open PRs for a repository
uv run python scripts/github_tools.py list octocat/hello-world

# Fetch diff, files, commits, or patch content for a specific PR
uv run python scripts/github_tools.py diff octocat/hello-world 1347
uv run python scripts/github_tools.py files octocat/hello-world 1347
uv run python scripts/github_tools.py commits octocat/hello-world 1347
uv run python scripts/github_tools.py patch octocat/hello-world 1347
```

All commands use the same environment configuration as the API (e.g., `GITHUB_TOKEN`, `GITHUB_API_URL`). Add `--output <file>` to save responses to disk, and `--per-page` / `--page` for pagination-aware commands.

---

## � Operational Modes

This system supports two distinct operational modes:

### 1. GitHub PR Mode (Requires GitHub Token)
**Use Case:** Review actual Pull Requests from GitHub repositories

**Requirements:**
- Valid `GITHUB_TOKEN` in `.env` file
- Network access to github.com
- Repository access (public repos work with no token, private require PAT with `repo` scope)

**API Request:**
```json
{
  "repo": "owner/repository",
  "pr_id": 123
}
```

**What Happens:**
1. Fetches PR metadata from GitHub REST API
2. Downloads the unified diff
3. Parses changed files
4. Filters supported languages
5. Runs multi-agent review
6. Returns structured comments

### 2. Manual Diff Mode (Fully Offline)
**Use Case:** Review code changes without GitHub (local dev, git hooks, other VCS)

**Requirements:**
- None! Works completely offline
- No GitHub token needed
- No network access required

**API Request:**
```json
{
  "diff": "diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n..."
}
```

**What Happens:**
1. Parses the provided diff string
2. Same filtering and review as GitHub mode
3. Returns structured comments

---

## 🌍 Supported Languages & Scope

### Fully Supported Languages
The agents are optimized for these languages and provide high-quality reviews:

- **Python** (`.py`)
- **JavaScript** (`.js`, `.jsx`, `.mjs`)
- **TypeScript** (`.ts`, `.tsx`)
- **Java** (`.java`)
- **Go** (`.go`)
- **Rust** (`.rs`)
- **C/C++** (`.c`, `.cpp`, `.h`, `.hpp`)
- **C#** (`.cs`)
- **Ruby** (`.rb`)
- **PHP** (`.php`)
- **Swift** (`.swift`)
- **Kotlin** (`.kt`, `.kts`)
- **Scala** (`.scala`)

### Automatically Ignored
- **Binary files** (images, PDFs, archives, executables)
- **Deleted files** (nothing to review)
- **Unsupported file types** (reported in `ignored_files` field)
- **Empty changes** (0 additions/deletions)

### Diff Size Limits
To ensure reasonable performance and avoid LLM context limits:

- **Max diff size:** 500 KB (configurable via `MAX_DIFF_SIZE_BYTES`)
- **Max lines:** 10,000 lines (configurable via `MAX_DIFF_LINES`)

**What happens when limits are exceeded:**
- API returns `413 Payload Too Large`
- Clear error message: "Diff exceeds maximum size of X KB/lines"
- Suggestion: Review smaller PRs or split into multiple reviews

---

## 🔐 Security & Best Practices

### Secret Management
✅ **DO**:
- Store all secrets in `.env` file (never committed to git)
- Use environment variables for tokens and API keys
- Rotate GitHub tokens regularly
- Use minimal required token scopes

❌ **DON'T**:
- Hardcode tokens in source code
- Commit `.env` to version control
- Share tokens in logs or API responses
- Use tokens with excessive permissions

### GitHub Token Scopes
**Recommended minimal scopes:**
- **Public repositories**: No token needed (rate-limited to 60 req/hr)
- **Private repositories**: `repo` scope (read access to code)

**How to create a token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "PR Review Agent - Read Only"
4. Select scopes:
   - For private repos: `repo` (full control) OR `repo:status` + `public_repo`
   - For public only: No scopes needed (just create the token)
5. Set expiration (30-90 days recommended)
6. Copy token immediately (shown only once)
7. Add to `.env`: `GITHUB_TOKEN=ghp_your_token_here`

### Log Security
This system automatically protects sensitive data:

- **GitHub tokens**: Never logged or returned in API responses
- **Full diffs**: Truncated in logs (first 200 chars only)
- **Sensitive patterns**: Auto-redacted (passwords, API keys in code)
- **Structured logging**: All logs are JSON with consistent fields for auditing

### Network Security
- All GitHub API calls use HTTPS
- No external LLM APIs (Ollama runs locally)
- Docker network isolation between services
- Non-root containers for all services

---

## ⚠️ Error Handling & Failure Modes

### Common Errors & Solutions

#### 422 Validation Error
**Symptom:** `{"detail": "Must provide either 'pr_id' + 'repo' OR 'diff'"}`
**Cause:** Missing or invalid request body
**Solution:** Provide either `pr_id` + `repo` (GitHub mode) OR `diff` (manual mode)

#### 404 PR Not Found
**Symptom:** `{"detail": "PR #123 not found in owner/repo"}`
**Causes:**
- PR doesn't exist
- Repository doesn't exist
- No access to private repo (check token)
**Solution:** Verify PR exists and token has access

#### 401/403 GitHub Authentication
**Symptom:** `{"detail": "GitHub authentication failed: invalid token or insufficient permissions"}`
**Causes:**
- Invalid token
- Expired token
- Insufficient scopes (need `repo` for private repos)
**Solution:** Check token and scopes at https://github.com/settings/tokens

#### 413 Diff Too Large
**Symptom:** `{"detail": "Diff exceeds maximum size of 500 KB"}`
**Cause:** PR is too large (massive file changes)
**Solution:** 
- Review smaller PRs
- Split PR into multiple smaller PRs
- Increase limits via env vars (may cause LLM timeouts)

#### 502 LLM Unavailable
**Symptom:** `{"detail": "LLM backend unavailable"}`
**Causes:**
- Ollama container not running
- Ollama not responding (OOM, crashed)
- Network issues between API and Ollama
**Solution:**
- Check Ollama health: `docker logs ollama`
- Restart: `docker-compose restart ollama`
- Pull model if missing: `docker exec -it ollama ollama pull qwen2.5-coder:3b`

#### Streamlit "API Unreachable"
**Symptom:** Red banner in Streamlit UI
**Causes:**
- API container not healthy
- Network issue in Docker
**Solution:**
- Check API health: `curl http://localhost:8000/health`
- View logs: `docker logs pr-review-api`
- Restart: `docker-compose restart api`

---

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add GITHUB_TOKEN if using GitHub mode

# 2. Build and start all services
docker-compose up --build -d

# 3. Pull the LLM model (first time only - takes 2-3 minutes)
docker exec -it ollama ollama pull qwen2.5-coder:3b

# 4. Check all services are healthy
docker-compose ps

# 5. Access the services
# - Streamlit UI: http://localhost:8501
# - Swagger API: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

### Services Overview

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **Ollama** | 11434 | Local LLM (qwen2.5-coder:3b) | `/api/tags` |
| **API** | 8000 | FastAPI backend | `/health` |
| **Streamlit** | 8501 | Web UI | `/_stcore/health` |
| **Prometheus** | 9090 | Metrics collection | `/-/healthy` |
| **Grafana** | 3000 | Dashboard visualization | `/api/health` |

### Checking Service Health

```bash
# All services status
docker-compose ps

# Individual service logs
docker logs pr-review-api -f
docker logs pr-review-streamlit -f
docker logs ollama -f

# Check API health directly
curl http://localhost:8000/health

# Check Streamlit health
curl http://localhost:8501/_stcore/health
```

### Stopping & Cleaning Up

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Remove unused Docker resources
docker system prune -f
```

---

## �📚 API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "pr-review-agent"
}
```

#### `GET /version`
Version and configuration information.

#### `GET /metrics`
Prometheus metrics endpoint.

#### `POST /review/pr`
Run a PR review either by providing a GitHub PR reference or a raw unified diff.

**Request Body**
```json
{
  "pr_id": 1347,
  "repo": "octocat/hello-world"
}
```
Or manual diff input:
```json
{
  "diff": "diff --git a/file.py b/file.py\n..."
}
```

**Successful Response**
```json
{
  "pr_id": 1347,
  "repo": "octocat/hello-world",
  "total_issues": 1,
  "critical_count": 0,
  "warning_count": 1,
  "info_count": 0,
  "comments": [
    {
      "file_path": "src/app/example.py",
      "line_number": 42,
      "severity": "warning",
      "category": "logic",
      "message": "Potential edge case not handled",
      "suggestion": "Add guard for empty input",
      "agent_name": "logic"
    }
  ]
}
```

If no `pr_id`/`repo` or `diff` is supplied the endpoint responds with HTTP 400.

---

## 🎨 Streamlit Web UI

For a user-friendly interface, access the Streamlit app at **http://localhost:8501** (when running via Docker Compose).

### Features
- **🔴 Red Review Button**: Prominent call-to-action for initiating reviews
- **Two Input Modes**:
  - **📦 GitHub PR Tab**: Enter `owner/repo` and PR number
  - **📝 Manual Diff Tab**: Paste any unified diff directly
- **Visual Issue Display**: Color-coded cards for each issue
  - 🔴 Critical issues (red background)
  - ⚠️ Warnings (yellow background)
  - ℹ️ Info (blue background)
- **API Health Status**: Real-time connection indicator in sidebar
- **Responsive Design**: Works on desktop and tablet

### Usage

#### GitHub PR Review
1. Navigate to the **📦 GitHub PR** tab
2. Enter repository (e.g., `octocat/hello-world`)
3. Enter PR number (e.g., `1347`)
4. Click the **🔴 Review PR** button
5. View categorized issues with file paths and suggestions

#### Manual Diff Review
1. Navigate to the **📝 Manual Diff** tab
2. Paste your unified diff (from `git diff`, `git show`, etc.)
3. Click the **🔴 Review Diff** button
4. View categorized issues with line numbers and suggestions

### Example Diff Input
```diff
diff --git a/src/app/example.py b/src/app/example.py
index 1234567..abcdefg 100644
--- a/src/app/example.py
+++ b/src/app/example.py
@@ -10,7 +10,7 @@ def process_data(items):
     for item in items:
-        if item is not None:
+        if item:
             results.append(item * 2)
     return results
```

### Screenshots
The UI displays:
- **Header**: "🤖 PR Review Agent" with tagline
- **Input Section**: Tabs for GitHub PR or manual diff
- **Review Button**: Large red button with "Review PR" or "Review Diff" text
- **Results Section**: Grouped by severity (Critical → Warning → Info)
- **Issue Cards**: Show file path, line number, category, message, and suggestion
- **Sidebar**: API health status (green ✅ / red ❌)

---

## 🔧 Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Environment Variables

```bash
# GitHub
GITHUB_TOKEN=your_token_here          # Optional for public repos, required for private
GITHUB_API_URL=https://api.github.com
GITHUB_TIMEOUT=15.0
GITHUB_USER_AGENT=CodeReview-Agent/0.1.0

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://ollama:11434   # Docker service name (use localhost:11434 for local dev)
OLLAMA_MODEL=qwen2.5-coder:3b         # Fast 3B parameter model for code review
OLLAMA_TIMEOUT=120.0                  # Generous timeout for reasoning

# Logging
LOG_LEVEL=info                        # debug, info, warning, error
LOG_FORMAT=json                       # json (production) or console (development)

# Server
PORT=8000
DEBUG=false

# Diff Limits (optional overrides)
MAX_DIFF_SIZE_BYTES=524288            # 500 KB default
MAX_DIFF_LINES=10000                  # 10K lines default
```

---

## 🧪 Testing

Run tests with pytest:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=html
```

---

## 📊 Monitoring

### Prometheus Metrics

Available at `/metrics` endpoint:
- Request count and latency
- Agent execution time
- Error rates

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (default credentials: admin/admin)

Pre-configured dashboards include:
- API performance
- Agent execution metrics
- System health

---

## 🛠️ Development

### Code Quality

```bash
# Format code (Ruff replaces Black)
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run all checks (pre-commit style)
uv run ruff format --check src/ tests/ && \
uv run ruff check src/ tests/ && \
uv run mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
uv run pre-commit install
```

---

## 📖 Project Structure

```
code-review-agent/
├── src/
│   └── app/
│       ├── api/              # API endpoints
│       ├── agents/           # AI agents
│       ├── core/             # Configuration & logging
│       ├── diff/             # Diff parsing
│       ├── github/           # GitHub integration
│       ├── llm/              # LLM client (Ollama)
│       ├── models/           # Pydantic models
│       ├── ui/               # Streamlit web interface
│       └── main.py           # FastAPI app
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data
├── docker/                   # Docker configs
├── grafana/                  # Grafana dashboards & datasources
├── scripts/                  # Utility scripts
├── .docs/                    # Additional documentation (excluded from git)
├── .github/                  # Core guidelines
├── pyproject.toml           # Dependencies
├── Dockerfile               # Multi-stage production image
└── docker-compose.yml       # 5-service orchestration
```

> **Note**: Additional implementation documentation and progress tracking files are available in `.docs/` folder (excluded from version control for cleaner repository structure).

---

## 🎓 Core Principles

This project follows strict software engineering principles:

1. **YAGNI**: Build only what's needed now
2. **SoC**: Clear separation of concerns across layers
3. **KISS**: Simple, maintainable solutions
4. **DRY**: Single source of truth for all logic
5. **Self-Documenting**: Type hints and clear naming

See `.github/copilot-instructions.md` for detailed guidelines.

---

## 📝 Phase 1 Checklist

- [x] Python 3.12 setup with UV
- [x] Project structure (src/, tests/, etc.)
- [x] Pydantic models (PR, FileDiff, CodeChunk, ReviewComment)
- [x] Settings management with pydantic-settings
- [x] Structured logging with structlog
- [x] FastAPI app with health endpoints
- [x] Prometheus metrics integration
- [x] Comprehensive .gitignore
- [x] Documentation (README.md)

---

## 🚧 Roadmap

### Phase 2: Docker & Containerization
- Multi-stage Dockerfile
- Docker Compose setup
- Prometheus & Grafana integration

### Phase 3: GitHub Integration
- GitHub API client
- Diff parser implementation
- PR fetching and parsing

### Phase 4: Agent Implementation
- Base agent architecture
- Specialized agent implementations
- Agent orchestration

### Phase 5: API Enhancement
- Review endpoint implementation
- Request/response validation
- Error handling

---

## 📄 License

[Add your license here]

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

---

## 📞 Contact

[Add contact information]

---

**Built with ❤️ as a personal learning project**
