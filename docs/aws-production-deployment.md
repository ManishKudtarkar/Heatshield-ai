# HeatShield AI — AWS Production Deployment Guide

**Document:** `docs/aws-production-deployment.md`
**Scope:** Deploying the HeatShield AI FastAPI backend (Strands Agents + Amazon Bedrock) and the Next.js dashboard to AWS for production.
**Target region:** Asia Pacific (Mumbai) — `ap-south-1`
**Foundation model:** Amazon Nova Lite via the Asia-Pacific cross-region inference profile `apac.amazon.nova-lite-v1:0`

> This is a deployment guide, not a deployment script. It describes the target architecture, the required AWS resources, and the concrete steps to stand them up. The repo's `infrastructure/` directory is intentionally left as the place to put the IaC for this (Terraform / AWS CDK / CloudFormation).

---

## 1. Target production architecture

```text
                           Internet
                              |
            +-----------------+-----------------+
            |                                   |
   +------------------+              +---------------------+
   |  CloudFront /    |              |   Route 53          |
   |  Amplify Hosting |              |   (app.example.com)  |
   |  (Next.js UI)    |              +---------------------+
   +------------------+
            |  (HTTPS, TLS via ACM)
            v
   +------------------+        +-------------------------------+
   | Application Load |        |  Amazon Bedrock               |
   | Balancer (HTTPS) |        |  (Nova Lite, ap-south-1 /     |
   |  -> ECS Fargate  | -----> |   apac inference profile)     |
   +------------------+        +-------------------------------+
            |                            ^
            |  outbound HTTPS            | AWS PrivateLink
            v                            | (interface VPC endpoint)
   +------------------+        +-------------------------------+
   |  Open-Meteo API  |        |  ECS Fargate (FastAPI)        |
   |  (weather data)  |        |  /  ECR  /  Secrets Manager   |
   +------------------+        |  /  CloudWatch Logs           |
                               +-------------------------------+
```

Two independently deployable services behind TLS:

- **Backend** — a containerized FastAPI app on **Amazon ECS Fargate** behind an **Application Load Balancer**. It calls **Amazon Bedrock** (private via an interface VPC endpoint) and **Open-Meteo** (public outbound HTTPS).
- **Frontend** — the Next.js dashboard on **AWS Amplify Hosting** (simplest) or as a container on ECS Fargate (full control). It calls the backend's public ALB URL.

Why ECS Fargate for the backend: predictable long-running process, simple health checks against the existing `/health` endpoint, and a natural fit for a Python process that holds a Strands/Bedrock client. Why Amplify for the frontend: git-push deploys with managed Next.js support and ACM/CDN built in.

---

## 2. Prerequisites

- An AWS account with admin or sufficient provisioning rights in `ap-south-1`.
- **Amazon Bedrock model access** for the Amazon Nova Lite foundation model (and the Asia-Pacific inference profile) requested in the AWS console under Bedrock → Model access. This is a per-account, per-region approval step.
- A registered domain in **Route 53** (or a domain you can delegate to it) for TLS certificates via **AWS Certificate Manager (ACM)**.
- Docker installed locally for building the backend image.
- A GitHub repository (the project already targets GitHub) for CI/CD.

---

## 3. Prepare the repository first

Before deploying, fix the repo-level issues that block a clean production build:

1. **Add pinned Python dependencies.** There is currently no `requirements.txt`/`pyproject.toml`; the README uses an inline, unpinned `pip install` list. Create `backend/requirements.txt` with pinned versions, e.g.:

   ```text
   strands-agents==1.62.0
   boto3==1.43.122
   fastapi==0.162.0
   uvicorn[standard]==0.54.0
   httpx==0.28.1
   pydantic==2.14.2
   pydantic-settings==2.16.2
   ```

2. **Make the backend read config from the environment, not hardcoded constants.** The agents currently hardcode `MODEL_ID = "apac.amazon.nova-lite-v1:0"` and `AWS_REGION = "ap-south-1"`, while `backend/.env` declares a *different* `BEDROCK_MODEL_ID=amazon.nova-lite-v1:0` that nothing loads. Pick one source of truth: load `BEDROCK_MODEL_ID`, `AWS_REGION`, and `APP_ENV` via `pydantic-settings` (already installed) and remove the `.env` mismatch. In production these come from the task environment (see §7), not a `.env` file.

3. **Stop committing Python bytecode.** Twenty `.pyc` files under `__pycache__/` are tracked in git even though the root `.gitignore` lists them. Untrack them:

   ```bash
   git rm -r --cached backend/app/**/__pycache__
   git commit -m "chore: stop tracking compiled Python bytecode"
   ```

4. **Add a backend Dockerfile** (see §5) and a `.dockerignore` that excludes `.venv`, `__pycache__`, `.env`, and `*.pyc`.

5. **Update CORS for production origins.** `backend/app/api.py` currently allows only `localhost:3000` and `127.0.0.1:3000`. Add the production frontend origin (or read it from an env var) before deploying.

---

## 4. IAM and least privilege

The backend's ECS task needs an **execution role** (to pull from ECR and write logs) and a **task role** (to call Bedrock at runtime). The task role is the security-critical one.

Minimum Bedrock permissions for the task role (Nova Lite generation via the inference profile):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvoke",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:ap-south-1::<foundation-model-id>",
        "arn:aws:bedrock:ap-south-1::/inference-profile/apac.amazon.nova-lite-v1:0"
      ]
    }
  ]
}
```

Notes:
- Use the **inference profile** ARN (`apac.amazon.nova-lite-v1:0`) for cross-region routing within Asia Pacific, which is what the code already expects.
- Do **not** grant `bedrock:*`; only the two invoke actions the app needs.
- If you use Secrets Manager/SSM for config, add a narrowly scoped read policy for the specific secret ARNs only.

The execution role needs `ecs-tasks:AssumeRole`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `logs:CreateLogStream`, `logs:PutLogEvents`.

---

## 5. Backend: containerize and run on ECS Fargate

### 5.1 Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Non-root user for defense in depth.
RUN useradd -r -u 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Gunicorn is not needed; uvicorn serves FastAPI directly.
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

`.dockerignore`:

```text
.venv
__pycache__
*.pyc
*.pyo
.env
.git
.pytest_cache
```

> The dev `--reload` flag must be removed for production (the CMD above omits it). Also bind to `0.0.0.0` so the ALB health checker can reach the container.

### 5.2 Build and push to Amazon ECR

```bash
AWS_REGION=ap-south-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO=heatshield-backend

aws ecr create-repository --repository-name $REPO --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t $REPO backend
docker tag $REPO $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
```

### 5.3 ECS cluster, task definition, and ALB

Provision (ideally via IaC):
- A VPC with at least two private subnets and two public subnets.
- A security group for the ALB (inbound 443 from the world) and one for the Fargate tasks (inbound 8000 only from the ALB SG).
- An **Application Load Balancer** with a TLS listener (ACM cert) targetting the Fargate service on port 8000.
- An **ECS Fargate cluster** (no EC2 capacity; Fargate is serverless).
- A **task definition** referencing the ECR image, the task role (§4), and runtime environment (§7).

Task definition essentials:

```json
{
  "family": "heatshield-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account>:role/heatshield-execution",
  "taskRoleArn": "arn:aws:iam::<account>:role/heatshield-task",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account>.dkr.ecr.ap-south-1.amazonaws.com/heatshield-backend:latest",
      "portMappings": [{ "containerPort": 8000 }],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/heatshield-backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

ALB target group health check: path `/health`, healthy threshold `2`, interval `30s`. The `/health` endpoint already exists in `app/api.py`.

Autoscaling: target tracking on ALB average CPU ~60%, with a minimum of 2 tasks for availability.

---

## 6. Frontend: Next.js dashboard

The dashboard is a client app that fetches the backend at runtime; `npm run build` prerenders `/` as static content. Two recommended paths, in order of simplicity:

### 6.1 AWS Amplify Hosting (recommended)

- Connect the GitHub repo to **AWS Amplify Hosting**, root directory `frontend`.
- Set the build command `npm run build` and the serve command `npm run start` (Amplify handles Next.js 16 SSR/static output).
- Set the environment variable `NEXT_PUBLIC_API_BASE_URL` to the backend ALB public URL (e.g. `https://api.heatshield.example.com`). Note: `NEXT_PUBLIC_*` values are baked into the build, so this must be set before build.
- Amplify provides the CDN and ACM TLS automatically on the Amplify domain.

### 6.2 ECS Fargate (full control)

Containerize the Next.js app (`node:22`-based image, `npm ci && npm run build`, `CMD ["npm","start"]`), push to ECR, and run on ECS Fargate behind an ALB + CloudFront, mirroring the backend pattern. Choose this if you want everything in one account/VPC with unified observability, or if Amplify's Next.js support lags a feature you need.

> Whichever path: `NEXT_PUBLIC_*` variables are **public** (visible in the browser). Never put secrets there. The only frontend config that belongs there is the backend's public API URL.

---

## 7. Configuration and secrets

The backend reads runtime config from the task environment, sourced from **AWS Secrets Manager** or **SSM Parameter Store** (never from a committed `.env`):

| Variable | Source | Example |
|---|---|---|
| `AWS_REGION` | Task env (plain) | `ap-south-1` |
| `BEDROCK_MODEL_ID` | Task env or Secrets Manager | `apac.amazon.nova-lite-v1:0` |
| `APP_ENV` | Task env (plain) | `production` |
| `CORS_ORIGINS` | Task env (plain) | `https://app.heatshield.example.com` |

Use the ECS task role to read secrets at startup rather than baking them into the image. For a small app, plain task environment variables (set on the task definition, not in the image) are acceptable for non-secret config; reserve Secrets Manager for anything sensitive.

Update `backend/app/api.py` CORS to read allowed origins from an env var instead of the hardcoded localhost list.

---

## 8. Networking and security hardening

- **Private subnets** for Fargate tasks; the ALB lives in public subnets.
- **Bedrock via PrivateLink**: create an interface VPC endpoint for `com.amazonaws.ap-south-1.bedrock-runtime` so model calls do not traverse the public internet. The Bedrock user guide documents PrivateLink connectivity for exactly this use case — see the references.
- **Outbound to Open-Meteo**: still requires public internet egress. Either a NAT Gateway (default for private subnets) or, to lock down further, an allow-listed VPC endpoint/proxy. For an initial production deploy, a single NAT Gateway is the pragmatic choice.
- **Security groups**: ALB SG inbound 443/0.0.0.0; task SG inbound 8000 from the ALB SG only; no other inbound.
- **AWS WAF** in front of the ALB (and Amplify, if supported) with the AWS-managed core rule set plus a rate-based rule to throttle `/api/v1/assess` (each assess call invokes Bedrock and costs money).
- **TLS**: ACM certificates for both `app.*` and `api.*`; enforce HTTPS, redirect HTTP→HTTPS at the ALB.
- **Guardrails on Bedrock**: enable Bedrock Guardrails for content safety on the invoked model, and set an AWS Budget + CloudWatch alarm on Bedrock usage to avoid runaway cost.

---

## 9. DNS and TLS

- **Route 53** hosted zone for your domain.
- Records: `app.heatshield.example.com` → Amplify/CloudFront; `api.heatshield.example.com` → backend ALB alias.
- **ACM** certificates (DNS validation) in `ap-south-1`. The ALB and CloudFront/Amplify reference these certs.

---

## 10. CI/CD

**Backend — GitHub Actions with OIDC to AWS (no long-lived keys):**

1. Create an OIDC identity provider in IAM for `https://token.actions.githubusercontent.com`.
2. Create a deploy role trusting your repo's `main` branch with a trust policy scoped to `repo:ManishKudtarkar/Heatshield-ai:ref:refs/heads/main`.
3. Workflow: build → `docker build` → `aws ecr get-login-password` → push to ECR → create new task-def revision → `aws ecs update-service --force-new-deployment`.

**Frontend — Amplify git-push:** pushing to `main` triggers an Amplify build automatically; no pipeline to maintain.

For a fully AWS-native alternative, use **CodePipeline + CodeBuild** for both.

---

## 11. Observability

- **CloudWatch Logs**: `/ecs/heatshield-backend` log group (already wired in the task def) and Amplify build/deploy logs.
- **Metrics & alarms**: ALB 5xx rate, target health check failures, Bedrock `Invocations` and `ThrottledRequests`, Fargate CPU/memory, and an alarm on `/health` failing targets.
- **Optional**: enable **AWS X-Ray** tracing on the FastAPI task to see the Bedrock call latency end-to-end.
- The backend already logs assessment requests at `INFO` via the `heatshield-api` logger; keep that and add structured fields if you need searchability.

---

## 12. Multi-environment and cost considerations

- **Environments**: separate stacks (or accounts) for `dev` / `staging` / `prod`, each with its own Bedrock model-access approval. Bedrock access is per-account-per-region, so you must request it in each environment.
- **Cost guardrails**: Fargate is billed per vCPU-second; two `512/1024` tasks run cheaply. The real cost driver is **Bedrock invocations** — put a WAF rate limit on `/api/v1/assess`, set an AWS Budget, and alarm on Bedrock spend. NAT Gateway has a fixed hourly cost plus per-GB; size accordingly.
- **Scaling**: start with 2 tasks, autoscale on CPU; Bedrock has account-level tokens-per-minute limits you can request increases for via Support.

---

## 13. Pre-deployment checklist

- [ ] `backend/requirements.txt` exists and is pinned.
- [ ] Backend reads `AWS_REGION` / `BEDROCK_MODEL_ID` / `CORS_ORIGINS` from env (no hardcoded `.env` mismatch).
- [ ] `.pyc` / `__pycache__` untracked from git.
- [ ] `backend/Dockerfile` and `.dockerignore` present; uvicorn binds `0.0.0.0` without `--reload`.
- [ ] CORS allows the production frontend origin.
- [ ] Bedrock model access approved for Nova Lite + the `apac` inference profile in `ap-south-1`.
- [ ] Task role least-privilege (only `bedrock:InvokeModel*` on the model + inference profile).
- [ ] Bedrock interface VPC endpoint created; no public-internet path for model calls.
- [ ] ALB `/health` target group health check configured.
- [ ] ACM certs + Route 53 records for `app.*` and `api.*`.
- [ ] WAF rate-based rule on `/api/v1/assess`.
- [ ] CloudWatch alarms on Bedrock throttling/spend and ALB 5xx.
- [ ] AWS Budget configured.
- [ ] Secrets in Secrets Manager/SSM, none in `NEXT_PUBLIC_*`.

---

## 14. Rollout and rollback

- **Backend**: ECS supports rolling deployments by default; set the minimum healthy percent to 100% and a controlled deployment circuit breaker so a failed health check rolls back automatically. For lower risk, run the new revision on a second target group behind a weighted forward rule (blue/green) and shift traffic after the health check passes.
- **Frontend**: Amplify keeps the previous deployment instantly revertible from the console.
- **Smoke test after deploy**: `curl https://api.heatshield.example.com/health` and one `POST /api/v1/assess` with the documented sample payload, checking that the response includes `safety_alerts` and the chosen `language`.

---

## 15. Cleanup / teardown

To avoid ongoing charges when decommissioning:

```bash
# Delete ECS service + cluster, ALB + target group, ECR repo
# Delete Route 53 records, ACM certs, Amplify app
# Delete VPC endpoints, NAT gateways, VPC
# Revoke Bedrock model access in the console
# Delete CloudWatch log groups and Secrets Manager secrets
```

Remove IaC-managed resources by destroying the stack (e.g. `terraform destroy` / `cdk destroy`) rather than deleting by hand where possible.

---

## 16. References

- Amazon Bedrock — Use interface VPC endpoints (AWS PrivateLink): https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html
- Access an AWS service using an interface VPC endpoint: https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpce-interface.html
- Amazon ECS on AWS Fargate: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
- Application Load Balancer: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html
- AWS Certificate Manager: https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
- Amazon Route 53: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- AWS Amplify Hosting (Next.js): https://docs.amplify.aws/react/
- AWS WAF: https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html
- GitHub Actions OIDC to AWS: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
- Strands Agents documentation: https://strandsagents.com/
- Amazon Bedrock documentation: https://docs.aws.amazon.com/bedrock/

---

## 17. What this guide does not cover

- A ready-to-run IaC implementation (the `infrastructure/` directory is the intended home for Terraform/CDK; this guide is the spec it should follow).
- Account-level Organizations / SCP hardening and AWS Backup policies — add per your security baseline.
- Multi-region active-active — the design targets a single region (`ap-south-1`) with the Asia-Pacific Bedrock inference profile handling regional model routing, which is sufficient for the current scope.
