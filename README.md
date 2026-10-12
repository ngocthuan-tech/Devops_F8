# Devops_F8 — DevOps Learning Log

![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=flat-square&logo=gnubash&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python%203.14-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![AWS](https://img.shields.io/badge/AWS%20VPC-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)

Hands-on assignments from a DevOps course, going from Linux basics to containerization and AWS network design. Each lesson lives in its own folder under [`assign/`](assign) with the task description and my solution.

## 📚 Lessons

| Lesson | Topic | What I built | Folder |
|---|---|---|---|
| Day 2 | Linux CLI | Basic file and directory operations from the terminal (`mkdir`, `cd`, `touch`, `nano`, `cat`) | [`assign/day2`](assign/day2) |
| Day 3 | Bash scripting | `health_check.sh`: loops over a list of services (Nginx, SSH), checks each with `systemctl is-active` and prints a warning when one is down | [`assign/day3`](assign/day3) |
| Day 4 | Docker basics | First Dockerfile for a Python app | [`assign/day4`](assign/day4) |
| Day 5–6 | Production Docker image | FastAPI + Poetry backend packaged as a production-ready image (details below) | [`assign/day5_6`](assign/day5_6) |
| Day 8 | AWS VPC design | Network design for 2 microservices (order & payment) in Tokyo: VPCs, subnets, route tables, NAT, peering, SGs, NACLs | [`assign/day8`](assign/day8) |

## ⭐ Highlights

### Production-grade Docker image (Day 5–6)

A hello-world FastAPI service, but packaged the way it would run in production:

- **Multi-stage build**: the `builder` stage installs Poetry and dependencies into a `.venv`; the `runtime` stage copies only the `.venv` and the app code, so Poetry and build caches never reach the final image.
- **Slim base image**: `python:3.14-slim`.
- **Non-root user**: the container runs as `appuser` (UID 1000), not root.
- **Healthcheck**: Docker probes `GET /health` every 30s.
- **Locked dependencies**: `pyproject.toml` + `poetry.lock` for reproducible builds.
- **Uvicorn with 2 workers**.

```bash
cd assign/day5_6
docker build -t hello-api .
docker run -d -p 8000:8000 --name hello-api hello-api
curl http://localhost:8000          # {"message":"Hello World"}
curl http://localhost:8000/health   # {"status":"ok"}
```

### AWS VPC design for microservices (Day 8)

Two teams, two services (order, payment), one database each, serving users in Japan:

- **Region** `ap-northeast-1` (Tokyo), spread across **2 AZs** (`1a`, `1c`) for high availability.
- **One VPC per service** (`10.10.0.0/16`, `10.20.0.0/16`) with non-overlapping CIDRs so they can be **peered**.
- **3 subnet tiers per AZ**: public (ALB, NAT), private app, private DB.
- **One NAT Gateway per AZ**, so losing an AZ does not cut the other AZ off from the Internet.
- **Least-privilege traffic**: Security Groups chain ALB → app → DB, only the order app subnets can reach the payment service, and DB subnets have no route outside the VPC.
- **NACLs** account for their stateless nature (ephemeral ports 1024–65535 opened for return traffic).

Full diagram and parameter tables: [`assign/day8/Readme.md`](assign/day8/Readme.md).

## 🧰 Environment

- Windows + Docker Desktop + VS Code
- Linux shell for the CLI and Bash lessons

---

Part of my path toward a Cloud / DevOps Engineer role. More on my [GitHub profile](https://github.com/ngocthuan-tech).
