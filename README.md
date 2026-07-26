# End-to-End Docker cagent Demo

This repository demonstrates an AI agent team diagnosing and fixing a real container runtime failure from end to end.

> Docker renamed **cagent** to **Docker Agent**. Docker Desktop 4.49 through 4.62 used the `cagent` name. Docker Desktop 4.63 and later uses the `docker agent` command.

## What the audience sees

A small Flask API works at `/`, but its Docker health check fails in production. The root agent reproduces the incident, inspects the application and container, forms a hypothesis, delegates a minimal patch to a fixer, asks a reviewer to validate it, rebuilds the image, and proves the service is healthy.

## Architecture

```text
Audience prompt
      |
      v
Root agent: investigate and coordinate
      |
      +--> Fixer: patch code and add regression test
      |
      +--> Reviewer: inspect diff and verification evidence
      |
      v
pytest + Docker build + Compose + HTTP health check
```

## Prerequisites

- Docker Desktop 4.63 or later, or a standalone Docker Agent installation
- An LLM provider API key, such as `OPENAI_API_KEY`
- Python 3.12+ for the host-side test, optional
- `curl`

Verify Docker Agent:

```bash
docker agent version
```

Set a provider key:

```bash
export OPENAI_API_KEY="your-key"
```

## Establish the broken baseline

```bash
docker compose up -d --build
curl -i http://localhost:8080/
curl -i http://localhost:8080/health
docker compose ps
docker compose logs orders-api
```

Expected result:

- `/` returns HTTP 200
- `/health` returns HTTP 503
- Compose eventually marks the container unhealthy

## Run the agent team

Interactive mode:

```bash
docker agent run agent.yaml
```

Paste this prompt:

```text
Investigate why the orders-api container is unhealthy. Reproduce the issue, identify the root cause, delegate the smallest safe fix, add a regression test, rebuild the image, and verify the running container. Do not stop at a code-level explanation. I need runtime evidence from the rebuilt container and an independent review of the patch.
```

Non-interactive mode:

```bash
docker agent run agent.yaml --exec \
  "Investigate why the orders-api container is unhealthy. Reproduce it, fix it with a regression test, rebuild it, verify /health, and review the final diff."
```

## Expected agent behavior

The root agent should discover that Compose sets `APP_ENV=production`, while `app/app.py` only treats `APP_ENV=prod` as healthy. A good fix should:

1. Make the health endpoint recognize the deployed environment value.
2. Add a test for `APP_ENV=production`.
3. Keep development behavior unchanged.
4. Run `pytest`.
5. Rebuild and restart the Compose service.
6. Verify that `/health` returns HTTP 200 and `{ "status": "ok" }`.
7. Ask the reviewer agent to inspect the patch and evidence.

## Manual verification

```bash
python -m pytest -q
docker compose up -d --build
curl --fail --silent http://localhost:8080/health
docker compose ps
```

Expected response:

```json
{"status":"ok"}
```

## Presenter script

### 1. Frame the problem

"The interesting part is not whether an LLM can spot a typo. The question is whether an agent can move through the full operational loop: reproduce, inspect, patch, test, rebuild, and verify the running container."

### 2. Show the failure

Run the baseline commands and point out that the application process is alive while the container is unhealthy. This separates process availability from application readiness.

### 3. Open `agent.yaml`

Explain:

- The root agent owns investigation and coordination.
- The fixer receives a narrow implementation task.
- The reviewer independently checks the diff and evidence.
- Filesystem and shell tools let the agents inspect code and execute the verification workflow.

### 4. Run Docker Agent

Use the prompt above. Let the audience watch the tool calls, delegation, file changes, tests, image rebuild, and final HTTP verification.

### 5. Inspect the evidence

```bash
git diff
python -m pytest -q
curl -i http://localhost:8080/health
docker compose ps
```

### 6. Close with the production lesson

"The value is not autonomous text generation. The value is an auditable execution path that connects a natural-language incident report to repository evidence and a verified runtime outcome."

## Demo reset

Commit the intentionally broken baseline before presenting. After each run:

```bash
git reset --hard HEAD
docker compose down --remove-orphans
```

## Optional extensions

- Add Docker MCP Toolkit search to let the investigator consult documentation.
- Run with `--sandbox` to confine shell execution.
- Push the agent configuration as an OCI artifact with `docker agent share push`.
- Replace the typo with a multi-service failure involving Redis or Postgres.
- Add a CI job that runs Docker Agent against a deliberately failing pull request.
