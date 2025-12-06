# CodeReview Agent — Demo Guide & Recording Script

## System Status Check (20–30s intro)

```bash
docker-compose ps
```

**Expected output:** All services HEALTHY or UP

---

## Part 1: GitHub PR Review via Streamlit (3 minutes)

### Setup
1. Open **Streamlit UI**: `http://localhost:8501`
2. Navigate to the **GitHub PR** tab

### Flow

**Input:**
- **Repository:** `your-username/code-review-agent`
- **PR Number:** `1` (will auto-increment as PRs are created)
- Click **Review PR**

**What to show:**
- The loading spinner (shows LLM reasoning in progress)
- Once complete: Highlight 2–3 agent comments:
  - **Logic Agent**: Division by zero risk in `calculate_average_metrics`
  - **Performance Agent**: O(n²) nested loop in `process_large_dataset`
  - **Readability Agent**: Poor variable naming (`a`, `b`, `c`, `d`)
- Mention: "4 agents analyzed this independently, caught different issues"

**Narration talking points:**
- "The system fetched the PR diff from GitHub, parsed the changed files, and ran 4 specialized agents in parallel."
- "Each agent focused on different concerns: Logic, Readability, Performance, and Security."
- "Notice how the agents caught distinct issues—division by zero, O(n²) loops, and unclear naming."

---

## Part 2: Manual Diff Review (1–1.5 minutes)

### Setup
1. Still in **Streamlit UI**, navigate to **Manual Diff** tab

### Flow

**Paste this diff:**
```diff
--- a/src/app/utils/database.py
+++ b/src/app/utils/database.py
@@ -1,6 +1,45 @@
+"""Database utilities with security vulnerabilities for demo."""
+
+import sqlite3
+
+
+def query_user_by_id(user_id, db_path="db.sqlite3"):
+    """Query user by ID - SQL injection vulnerability."""
+    conn = sqlite3.connect(db_path)
+    cursor = conn.cursor()
+    
+    # SECURITY ISSUE: SQL injection vulnerability!
+    # User input directly interpolated into query
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    
+    cursor.execute(query)
+    result = cursor.fetchone()
+    conn.close()
+    
+    return result
+
+
+def authenticate_user(username, password):
+    """Authenticate user with hardcoded credentials."""
+    # SECURITY ISSUE: Hardcoded credentials in code!
+    ADMIN_USERNAME = "admin"
+    ADMIN_PASSWORD = "SuperSecret123!"
+    
+    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
+        return {"authenticated": True, "role": "admin"}
+    
+    return {"authenticated": False}
```

Click **Review Diff**

**What to show:**
- SecurityAgent highlights SQL injection in `query_user_by_id`
- SecurityAgent flags hardcoded credentials in `authenticate_user`
- Read aloud: "SQL injection here—user input directly in the f-string. Should use parameterized queries."
- Highlight the suggestion: "Use `cursor.execute(query, (user_id,))` instead."

**Narration talking points:**
- "Now let's test with a raw diff of new code containing security vulnerabilities."
- "The Security Agent immediately caught the SQL injection—direct string interpolation in a database query."
- "It also flagged hardcoded credentials, which is a classic security anti-pattern."
- "Notice the agent provided a specific, actionable suggestion."

---

## Part 3: Swagger / Architecture Flash (1 minute)

### Setup
Open **Swagger UI**: `http://localhost:8000/docs`

### Flow

**Show:**
- The `/review/pr` endpoint documentation
- Input parameters: `pr_id`, `repo`, `diff` (note the union type)
- Response schema: Array of `ReviewComment` objects with fields: `file_path`, `line_number`, `severity`, `category`, `message`, `suggestion`

**Optionally show architecture diagram** (if you have a slide):
- GitHub API → Diff Parser → Agents (Logic, Readability, Performance, Security) → Ollama LLM → Response

**Narration talking points:**
- "The API supports two modes: GitHub PR review via PR ID, or raw diff input."
- "Each agent specializes in one domain, analyzing the same code chunks in parallel."
- "The LLM (Ollama, running locally) powers the reasoning; no external API calls, fully on-device."

---

## Part 4: Grafana Live Metrics (20–30s)

### Setup
Open **Grafana**: `http://localhost:3000` (login: `admin`/`admin`)

### Flow

**Navigate to Dashboard:** "CodeReview Agent Metrics"

**Show these panels:**
1. **Request Rate** (requests/sec) — should show spikes from the 2 reviews you just ran
2. **P95 Latency** (ms) — should be 1000–3000ms per review (LLM reasoning time)
3. **Success Rate** (%) — should be 100% if no errors
4. **Endpoint Distribution** — `/review/pr` should be the dominant endpoint

**Narration talking points:**
- "This is our Prometheus-scraped metrics dashboard."
- "You can see the spike in request rate and latency from the two reviews we just ran."
- "In production, this lets us monitor agent performance, detect anomalies, and catch errors in real-time."

---

## Part 5: Optional Quick Mention of Tests (20–30s, can be overlay or after recording)

**Show output:**
```bash
docker-compose run --rm api pytest --tb=short -q
```

**Or cite:**
- 62/62 tests passing
- 90%+ coverage on core agents
- Type checking (mypy) clean
- Linting (ruff) clean

**Narration:**
- "Behind the scenes, we've got 62 integration + unit tests, 90% coverage on core logic, and strict type checking."

---

## Command Reference for Copy/Paste During Recording

```bash
# Check system status
docker-compose ps

# Run tests (if needed for overlay)
docker-compose run --rm api pytest --tb=short -q

# Restart services if needed
docker-compose down
docker-compose up -d

# Check Ollama is running
curl http://localhost:11434/api/tags
```

### URLs for Recording
- **Streamlit:** http://localhost:8501
- **Swagger:** http://localhost:8000/docs
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090

---

## Recording Checklist

- [ ] All services healthy (docker-compose ps)
- [ ] Streamlit loaded and accessible
- [ ] GitHub PR created (feature/logic-perf-issues)
- [ ] Manual diff copied and ready to paste
- [ ] Grafana dashboard visible and metrics showing
- [ ] Screen recording software ready
- [ ] Microphone/audio capture enabled
- [ ] Run rehearsal once without recording
- [ ] Record final take (aim for 5–7 min total)
- [ ] Keep command snippets in text file for pasting

---

## Troubleshooting

**Streamlit not responding?**
```bash
docker-compose restart ui
```

**No metrics in Grafana?**
```bash
docker-compose logs -f prometheus
# Check if /metrics endpoint returns data
curl http://localhost:8000/metrics | grep review_pr
```

**Ollama not running?**
```bash
docker-compose logs ollama
curl http://localhost:11434/api/tags
```

**API errors?**
```bash
docker-compose logs -f api
```

---

## Final Notes

- **Keep it simple:** No code changes, no tweaks. Show what's already built.
- **Focus on value:** Logic bugs, security issues, real monitoring.
- **Time it:** Streamlit (3 min) + Diff (1.5 min) + Swagger (1 min) + Grafana (0.5 min) = ~6 min.
- **Narrate confidently:** You've built something solid; just show it.
- **Multiple takes are OK:** This isn't live. Redo if you stumble or want to tighten pacing.

