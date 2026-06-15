# AWS Club — Step-by-Step Lab Guide

**Workshop duration:** 4 hours  
**Region used in examples:** `eu-central-1` (Frankfurt) — change if your instructor uses another region.  
**Lab assets:** `lab-assets/lab-a-s3/index.html`, `lab-assets/lab-0-verify-identity/iam-lab-policy.json`, `lab-assets/lab-d-sqs/`

---

## Before you start

### What you need

| Item | Details |
|------|---------|
| Laptop | Windows, macOS, or Linux |
| Browser | Chrome or Edge recommended |
| AWS access | Lab IAM user credentials (Access Key ID + Secret) **or** instructor-provided account |
| Files | Download `index.html` from `materials/lab-assets/lab-a-s3/` |
| Optional | AWS CLI v2 installed |

### Naming convention

- S3 bucket: `aws-club-<your-initials>-<YYYYMMDD>` (lowercase, no spaces)
- Example: `aws-club-am-20260602`

### Pair roles

| Role | Responsibility |
|------|----------------|
| **Partner A** | AWS Console navigation |
| **Partner B** | Terminal / AWS CLI |

Swap roles in Lab B.

---

## Lab 0 — Verify identity (10 min)

**Goal:** Confirm you are signed in as the lab IAM user and (optional) CLI works.

### Part A — AWS Console

1. Open https://console.aws.amazon.com/
2. Sign in with your **lab IAM user** (not root).
3. Top-right: note the **Region** dropdown → select **Europe (Frankfurt) eu-central-1** (or instructor’s region).
4. Search bar → type **IAM** → open **IAM**.
5. Left menu → **Users** → click your username.
6. **Record** your username: `________________`

**Expected:** You see your user summary without “root” in the account email.

### Part B — AWS CLI (Partner B)

**Install (if needed):**

- Windows: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html  
- Mac: `brew install awscli`  
- Linux: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip` (see AWS docs)

**Configure:**

```bash
aws configure
```

| Prompt | Enter |
|--------|--------|
| AWS Access Key ID | (from instructor) |
| AWS Secret Access Key | (from instructor) |
| Default region name | `eu-central-1` |
| Default output format | `json` |

**Verify:**

```bash
aws sts get-caller-identity
```

**Expected output (example):**

```json
{
    "UserId": "AIDAXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/aws-club-student01"
}
```

**Troubleshooting:**

| Problem | Fix |
|---------|-----|
| `Unable to locate credentials` | Run `aws configure` again |
| `AccessDenied` | Ask instructor to attach lab policy |
| Wrong region later | `export AWS_DEFAULT_REGION=eu-central-1` (Mac/Linux) or set in configure |

**Checkpoint ☐** Console login works  
**Checkpoint ☐** `get-caller-identity` shows your lab user ARN

---

## Lab A — Amazon S3 (25 min)

**Goal:** Create a bucket, upload a file via Console and CLI, enable versioning.

### Step A1 — Create a bucket (Console — Partner A)

1. Console search → **S3** → open **S3**.
2. Click **Create bucket**.
3. **Bucket name:** `aws-club-<initials>-<date>` (must be globally unique).
4. **AWS Region:** `eu-central-1`.
5. **Object Ownership:** ACLs disabled (recommended) — leave default.
6. **Block Public Access:** leave **all four checked** (recommended for lab).
7. **Bucket Versioning:** Disable for now (enable in Step A5).
8. **Encryption:** SSE-S3 (default) is fine.
9. Click **Create bucket**.

**Expected:** Bucket appears in the list.

**Troubleshooting:**

| Problem | Fix |
|---------|-----|
| `Bucket name already exists` | Add more characters (middle name, random digits) |
| `Access Denied` | Instructor must allow `s3:CreateBucket` for your prefix |

**Record bucket name:** `________________`

---

### Step A2 — Upload `index.html` (Console)

1. Click your bucket name.
2. Tab **Objects** → **Upload**.
3. **Add files** → select `index.html` from `lab-assets/lab-a-s3/`.
4. Scroll down → **Upload**.
5. Click the object `index.html` → under **Object overview**, copy the **S3 URI** (e.g. `s3://aws-club-am-20260602/index.html`).

**Checkpoint ☐** Object listed in bucket

---

### Step A3 — Upload via CLI (Partner B)

Open terminal in the folder containing `index.html`:

```bash
aws s3 cp index.html s3://YOUR-BUCKET-NAME/index.html
```

Replace `YOUR-BUCKET-NAME` with your actual bucket.

**List objects:**

```bash
aws s3 ls s3://YOUR-BUCKET-NAME/
```

**Expected:**

```
2026-06-02 14:30:00        612 index.html
```

**Optional — sync a folder:**

```bash
aws s3 sync ./lab-assets/lab-a-s3 s3://YOUR-BUCKET-NAME/demo/
```

---

### Step A4 — Download back (CLI)

```bash
aws s3 cp s3://YOUR-BUCKET-NAME/index.html ./downloaded-index.html
```

Open `downloaded-index.html` locally — content should match.

---

### Step A5 — Enable versioning (Console)

1. Bucket → tab **Properties**.
2. Section **Bucket Versioning** → **Edit**.
3. Select **Enable** → **Save changes**.
4. Upload `index.html` again (overwrite).
5. Object → **Show versions** — you should see two versions.

**Discussion point:** Versioning helps recovery from accidental delete/overwrite.

---

### Step A6 — Takeaway artifact

1. Take a **screenshot** of the S3 objects list showing `index.html`.
2. Paste into the club shared doc **or** save locally for portfolio.

**Checkpoint ☐** Bucket created  
**Checkpoint ☐** Upload via Console  
**Checkpoint ☐** Upload/list via CLI  
**Checkpoint ☐** Versioning enabled  

---

## Lab B — VPC + EC2 + nginx (40 min)

**Goal:** Create a VPC with a public subnet, launch **one** Amazon Linux instance, connect with SSH, and serve a welcome page that shows this machine's **private IP** and **hostname**.

**Assets:**

| File | Purpose |
|------|---------|
| `lab-assets/lab-b-ec2/index.html` | Welcome page (placeholders filled by nginx at serve time) |
| `lab-assets/lab-b-ec2/nginx-lab-snippet.conf` | `sub_filter` lines → `/etc/nginx/default.d/aws-club-lab.conf` |

### Step B1 — Create VPC (Console)

1. Console search → **VPC** → **Your VPCs** → **Create VPC**.
2. **VPC settings:** **VPC only** (not the wizard — we build each piece).
3. **Name:** `aws-club-<initials>-vpc`
4. **IPv4 CIDR:** `10.0.0.0/16`
5. **Create VPC**.

**Record VPC ID:** `vpc-________________`

---

### Step B2 — Internet gateway (Console)

1. VPC → **Internet gateways** → **Create internet gateway**.
2. **Name:** `aws-club-<initials>-igw`
3. **Create**.
4. Select the IGW → **Actions** → **Attach to VPC** → choose `aws-club-<initials>-vpc`.

---

### Step B3 — Public subnet (Console)

1. VPC → **Subnets** → **Create subnet**.
2. **VPC:** `aws-club-<initials>-vpc`
3. **Subnet name:** `aws-club-<initials>-public`
4. **Availability Zone:** pick one (e.g. `eu-central-1a`)
5. **IPv4 CIDR:** `10.0.1.0/24`
6. **Create subnet**.
7. Select the subnet → **Actions** → **Edit subnet settings** → enable **Enable auto-assign public IPv4 address** → **Save**.

---

### Step B4 — Public route table (Console)

1. VPC → **Route tables** → find the table associated with your VPC (not the main/default association yet).
2. Select it → **Subnet associations** → **Edit subnet associations** → check `aws-club-<initials>-public` → **Save**.
3. **Routes** tab → **Edit routes** → **Add route**:
   - Destination: `0.0.0.0/0`
   - Target: your Internet gateway
4. **Save changes**.

---

### Step B5 — Create a key pair (Console)

1. Console search → **EC2** → **Key pairs** (under Network & Security).
2. **Create key pair**.
3. **Name:** `aws-club-<initials>-key`
4. **Key pair type:** RSA
5. **Private key format:** `.pem` (Mac/Linux) or `.ppk` if PuTTY-only on Windows
6. **Create** → file downloads automatically.

**Secure the key:**

**macOS / Linux:**

```bash
chmod 400 ~/Downloads/aws-club-xx-key.pem
mv ~/Downloads/aws-club-xx-key.pem ~/.ssh/
```

**Windows (PowerShell):**

```powershell
icacls "$env:USERPROFILE\Downloads\aws-club-xx-key.pem" /inheritance:r
icacls "$env:USERPROFILE\Downloads\aws-club-xx-key.pem" /grant:r "$env:USERNAME:R"
```

**Never** upload `.pem` to Git or Discord.

---

### Step B6 — Create security group (Console)

1. EC2 → **Security Groups** → **Create security group**.
2. **Name:** `aws-club-<initials>-sg`
3. **VPC:** `aws-club-<initials>-vpc` (your VPC, not default)
4. **Inbound rules:**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | **My IP** | Admin access |
| HTTP | 80 | 0.0.0.0/0 | Lab web demo |

5. **Outbound:** leave default (All traffic → 0.0.0.0/0).
6. **Create security group**.

**Record security group ID:** `sg-________________`

---

### Step B7 — Launch EC2 instance (Console)

1. EC2 → **Instances** → **Launch instances**.
2. **Name:** `aws-club-<initials>-web1`
3. **AMI:** Amazon Linux 2023 (free tier eligible)
4. **Instance type:** `t3.micro`
5. **Key pair:** select the key you created
6. **Network:** `aws-club-<initials>-vpc`, subnet `aws-club-<initials>-public`, **Auto-assign public IP: Enable**
7. **Security group:** Select existing → `aws-club-<initials>-sg`
8. **Storage:** 8 GiB gp3 (default)
9. **Launch instance**.
10. Wait until **Instance state** = **Running**.

**Record:**

| Field | Value |
|-------|--------|
| Instance ID | `i-________________` |
| Public IPv4 address | `________________` |
| Private IPv4 address | `10.0.1.x` (verify in console) |

---

### Step B8 — Connect with SSH (Partner B)

**macOS / Linux:**

```bash
ssh -i ~/.ssh/aws-club-xx-key.pem ec2-user@YOUR_PUBLIC_IP
```

**Windows (OpenSSH, build 1809+):**

```powershell
ssh -i $env:USERPROFILE\Downloads\aws-club-xx-key.pem ec2-user@YOUR_PUBLIC_IP
```

**First connection:** type `yes` when asked about host key fingerprint.

**Expected prompt:**

```
[ec2-user@ip-10-0-1-xx ~]$
```

**Troubleshooting:**

| Problem | Fix |
|---------|-----|
| `Permission denied (publickey)` | Wrong key, wrong user (`ec2-user`), or chmod 400 / icacls missing |
| `Connection timed out` | SG allows SSH from **My IP**? Instance running? Public subnet + IGW route? Correct public IP? |
| `Network unreachable` | Campus Wi‑Fi blocking port 22 — try hotspot or ask instructor |

---

### Step B9 — Install nginx and enable dynamic placeholders (on EC2)

```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

**Expected:** `active (running)`.

On **Amazon Linux 2023** there is no `/etc/nginx/conf.d/default.conf`. The default server block is in `/etc/nginx/nginx.conf` and loads snippets from `/etc/nginx/default.d/`.

Create `/etc/nginx/default.d/aws-club-lab.conf` (content from `lab-assets/lab-b-ec2/nginx-lab-snippet.conf`):

```bash
sudo tee /etc/nginx/default.d/aws-club-lab.conf <<'EOF'
location / {
    gzip off;
    sub_filter_types text/html;
    sub_filter '__PRIVATE_IP__' '$server_addr';
    sub_filter '__HOSTNAME__' '$hostname';
    sub_filter_once off;
}
EOF
```

Reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Verify on the instance** (must show `ip-10-0-1-xx`, **not** `__PRIVATE_IP__`):

```bash
curl -s http://localhost | grep -E 'ip-10|__PRIVATE'
```

nginx replaces placeholders **when serving the page**, so the same `index.html` works on every instance without per-machine editing.

> **Troubleshooting — page still shows `__PRIVATE_IP__`?**
> 1. Confirm the snippet loaded: `sudo nginx -T 2>/dev/null | grep -A6 aws-club-lab`
> 2. **`gzip off` is required** — `sub_filter` is skipped on gzipped responses (common on AL2023).
> 3. Reload after edits: `sudo nginx -t && sudo systemctl reload nginx`
> 4. Hard-refresh the browser (Ctrl+Shift+R) or try a private window.

**Next → Step B10:** copy `lab-assets/lab-b-ec2/index.html` into `/usr/share/nginx/html/`.

---

### Step B10 — Add `index.html` to the web server

Deploy the lab welcome page from `lab-assets/lab-b-ec2/index.html` into nginx’s document root (`/usr/share/nginx/html/`).

**B10.1 — Copy `index.html` to the instance (on your laptop)**

From the `materials` folder:

```bash
scp -i ~/.ssh/aws-club-xx-key.pem lab-assets/lab-b-ec2/index.html ec2-user@YOUR_PUBLIC_IP:~/
```

**B10.2 — Install `index.html` as the site home page (on EC2, over SSH)**

```bash
sudo cp ~/index.html /usr/share/nginx/html/index.html
sudo chmod 644 /usr/share/nginx/html/index.html
ls -l /usr/share/nginx/html/index.html
```

**B10.3 — Quick check (still on EC2)**

```bash
curl -s http://localhost | grep -E 'AWS Club|__PRIVATE_IP__|ip-10'
```

**Expected:** HTML contains **Welcome to the AWS Club!** and a hostname like `ip-10-0-1-xx` (placeholders already replaced by nginx).

> Without this step, nginx serves its generic default page — not the lab welcome page.

---

### Step B11 — Test in browser (Partner A)

1. On your laptop browser: `http://YOUR_PUBLIC_IP`
2. **Expected:** Welcome page titled **Welcome to the AWS Club!** with private IP `10.0.1.x` and hostname `ip-10-0-1-xx` displayed.

**Optional — test from EC2:**

```bash
curl -s http://localhost | grep ip-10
```

---

### Step B12 — ★ Stretch: EC2 via CLI (Partner B)

On your laptop:

```bash
aws ec2 describe-instances \
  --instance-ids i-YOUR_INSTANCE_ID \
  --query "Reservations[0].Instances[0].[State.Name,PublicIpAddress,PrivateIpAddress,InstanceType]" \
  --output table
```

---

### Step B13 — Tag your instance (Console)

1. Instances → select your instance → **Tags** tab → **Manage tags**.
2. Add: Key `Project`, Value `aws-club-lab`.

**Checkpoint ☐** VPC + public subnet + IGW route  
**Checkpoint ☐** Instance running  
**Checkpoint ☐** SSH works  
**Checkpoint ☐** `index.html` in `/usr/share/nginx/html/`  
**Checkpoint ☐** Welcome page shows private IP and hostname  

---

## Lab C — Second EC2 + Application Load Balancer (35 min)

**Goal:** Launch a second web server, then place both instances behind an **Application Load Balancer**. With stickiness **disabled**, refreshing the ALB URL shows a **different hostname** — proof that requests hit different machines.

**Assets:** same `lab-assets/lab-b-ec2/index.html` and `nginx-lab-snippet.conf` (see also `lab-assets/lab-c-alb/README.md`).

### Step C1 — Second public subnet (Console)

ALB requires subnets in **at least two Availability Zones**.

1. VPC → **Subnets** → **Create subnet**.
2. **VPC:** `aws-club-<initials>-vpc`
3. **Name:** `aws-club-<initials>-public-b`
4. **AZ:** different from Lab B (e.g. `eu-central-1b`)
5. **CIDR:** `10.0.2.0/24`
6. Enable **auto-assign public IPv4**.
7. Associate with the **same public route table** used in Lab B (route to IGW).

---

### Step C2 — Launch second EC2 (Console)

1. EC2 → **Launch instances**.
2. **Name:** `aws-club-<initials>-web2`
3. **AMI / type:** Amazon Linux 2023, `t3.micro` (same as web1)
4. **Subnet:** `aws-club-<initials>-public-b`
5. **Security group:** same `aws-club-<initials>-sg` as web1
6. **Launch** → record **Public IPv4** of web2.

---

### Step C3 — Configure web2 (SSH)

Repeat Lab B Steps B8–B10 on **web2**:

1. SSH into web2
2. Install nginx + create `/etc/nginx/default.d/aws-club-lab.conf` from `nginx-lab-snippet.conf`
3. Copy the **same** `index.html` to `/usr/share/nginx/html/`
4. Verify `http://WEB2_PUBLIC_IP` shows a **different hostname** than web1

---

### Step C4 — Create target group (Console)

1. EC2 → **Target Groups** → **Create target group**.
2. **Target type:** Instances
3. **Name:** `aws-club-http-tg`
4. **Protocol:** HTTP, **Port:** 80, **VPC:** `aws-club-<initials>-vpc`
5. **Health check path:** `/`
6. **Register targets:** select **web1** and **web2** → **Include as pending**
7. **Create target group**.
8. **Attributes** → **Stickiness** → ensure **Load balancer generated cookie** is **Off** (default).

Wait until both targets show **Healthy** (1–2 min).

---

### Step C5 — ALB security group (Console)

1. EC2 → **Security Groups** → **Create security group**.
2. **Name:** `aws-club-<initials>-alb-sg`
3. **VPC:** yours
4. **Inbound:** HTTP 80 from `0.0.0.0/0`
5. **Create**.

(Your instance SG already allows HTTP 80 from anywhere, so targets accept ALB traffic.)

---

### Step C6 — Create Application Load Balancer (Console)

1. EC2 → **Load Balancers** → **Create load balancer** → **Application Load Balancer**.
2. **Name:** `aws-club-alb`
3. **Scheme:** Internet-facing
4. **Network mapping:** `aws-club-<initials>-vpc`, select **both** public subnets (different AZs)
5. **Security group:** `aws-club-<initials>-alb-sg`
6. **Listener:** HTTP :80 → forward to `aws-club-http-tg`
7. **Create load balancer**.

**Record ALB DNS name:** `aws-club-alb-XXXX.eu-central-1.elb.amazonaws.com`

---

### Step C7 — Test load balancing

1. Browser: `http://<ALB-DNS-NAME>/`
2. **Refresh 5–10 times** — the **hostname** and **private IP** on the page should **alternate** between web1 and web2.
3. ★ **Stretch:** `sudo systemctl stop nginx` on one instance → target becomes **unhealthy** → only one hostname appears.

**Checkpoint ☐** web2 serves same page with different hostname  
**Checkpoint ☐** Target group: both healthy, stickiness off  
**Checkpoint ☐** ALB URL alternates hostname on refresh  

---

## Lab D — Amazon SQS (25 min)

**Goal:** Create a queue, then run a **publisher** on **web1** and a **subscriber** on **web2**. The publisher sends a JSON message every 5 seconds with an incrementing `count`; the subscriber long-polls the queue and appends each message to a log file.

**Prerequisites:** Lab B (web1) and Lab C (web2) instances running.

**Assets:** `lab-assets/lab-d-sqs/publisher.py`, `lab-assets/lab-d-sqs/subscriber.py` (see also `lab-assets/lab-d-sqs/README.md`).

```
web1 (publisher)  ──send──▶  SQS queue  ──poll──▶  web2 (subscriber → sqs-messages.log)
```

---

### Step D1 — Create SQS queue (Console — Partner A)

1. Console search → **SQS** → open **Amazon SQS**.
2. Click **Create queue**.
3. **Type:** Standard
4. **Name:** `aws-club-<initials>-queue`
5. Leave other settings at defaults → **Create queue**.
6. Open the queue → copy the **URL** (starts with `https://sqs.eu-central-1.amazonaws.com/...`).

**Record queue URL:** `________________`

**Expected:** Queue status **Active**, messages available **0**.

---

### Step D2 — AWS credentials on EC2 (both instances)

The Python apps use **boto3**, which reads the same credentials as the AWS CLI.

On **web1** and **web2** (SSH), run once per instance if not already configured:

```bash
aws configure
```

Use the same lab IAM user keys and region `eu-central-1` as on your laptop.

**Verify on each instance:**

```bash
aws sts get-caller-identity
aws sqs get-queue-attributes --queue-url "YOUR-QUEUE-URL" --attribute-names QueueArn
```

**Troubleshooting:**

| Problem | Fix |
|---------|-----|
| `AccessDenied` on SQS | Ask instructor to attach updated lab policy (`sqs:*` on `aws-club-*` queues) |
| `Unable to locate credentials` | Run `aws configure` on that EC2 instance |

---

### Step D3 — Install boto3 (both instances)

Amazon Linux 2023:

```bash
sudo dnf install -y python3-boto3
python3 -c "import boto3; print(boto3.__version__)"
```

---

### Step D4 — Copy lab scripts (from your laptop)

From the `materials` folder:

```bash
scp -i ~/.ssh/aws-club-xx-key.pem lab-assets/lab-d-sqs/publisher.py ec2-user@WEB1_PUBLIC_IP:~/
scp -i ~/.ssh/aws-club-xx-key.pem lab-assets/lab-d-sqs/subscriber.py ec2-user@WEB2_PUBLIC_IP:~/
```

---

### Step D5 — Run the publisher on web1

SSH into **web1**:

```bash
export SQS_QUEUE_URL="https://sqs.eu-central-1.amazonaws.com/ACCOUNT/aws-club-xx-queue"
chmod +x ~/publisher.py
python3 ~/publisher.py
```

**Expected:** Every 5 seconds, a line like `Sent #3 MessageId=...` with an increasing count.

Leave this terminal running.

---

### Step D6 — Run the subscriber on web2

Open a **second SSH session** to **web2**:

```bash
export SQS_QUEUE_URL="https://sqs.eu-central-1.amazonaws.com/ACCOUNT/aws-club-xx-queue"
chmod +x ~/subscriber.py
python3 ~/subscriber.py
```

In another web2 session (or after a few seconds):

```bash
tail -f ~/sqs-messages.log
```

**Expected:** Log lines with increasing `count=` values and `hostname=ip-10-0-...` from web1.

Example line:

```
2026-06-07T14:32:10+00:00 count=4 hostname=ip-10-0-1-42 body={"count": 4, "hostname": "ip-10-0-1-42", ...}
```

---

### Step D7 — Console check (Partner A)

1. SQS → your queue → **Monitoring** tab — **Number of messages sent** increases.
2. **Send and receive messages** → **Poll for messages** — should be empty (subscriber deleted them).

---

### Step D8 — ★ Stretch: CLI send (Partner B)

From your laptop:

```bash
aws sqs send-message \
  --queue-url "YOUR-QUEUE-URL" \
  --message-body '{"count": 999, "message": "Hello from CLI"}'
```

Watch web2 subscriber print the message and append to the log.

---

### Step D9 — Stop apps

On web1 and web2: **Ctrl+C** in the terminal running the Python script.

**Checkpoint ☐** Queue created  
**Checkpoint ☐** Publisher sends counted messages every 5 s  
**Checkpoint ☐** Subscriber log shows increasing counts from web1 hostname  
**Checkpoint ☐** Console monitoring shows messages flowing  

---

### Optional — RDS console tour (5 min, instructor-led)

If time allows after Lab D:

1. Console → **RDS** → **Databases** → open instructor’s demo DB.
2. Note: **Endpoint**, **Engine** (e.g. MySQL), **VPC security group**.
3. Discuss: DB in **private subnet**; only app tier (EC2 SG) allowed on port 3306.

---

## Tear-down (mandatory — 15 min before end)

### Delete load balancer (Lab C)

1. EC2 → **Load Balancers** → select `aws-club-alb` → **Delete**.
2. EC2 → **Target Groups** → select `aws-club-http-tg` → **Delete**.

### Delete SQS queue (Lab D)

1. SQS → select `aws-club-<initials>-queue` → **Delete**.
2. Confirm by typing `delete`.

### Terminate EC2

1. EC2 → **Instances** → select **web1** and **web2**.
2. **Instance state** → **Terminate instance** → confirm.
3. Wait until **Terminated**.

### Delete VPC resources (Lab B/C)

1. Detach and delete **Internet gateway**.
2. Delete **subnets** and **route tables** (if not auto-removed).
3. Delete **security groups** and **VPC**.

### Delete key pair (optional)

EC2 → **Key pairs** → delete lab key (only after instances terminated).

### S3 cleanup (if allowed)

1. Bucket → select all objects → **Delete**.
2. **Empty** bucket version delete if prompted.
3. **Delete bucket** (or leave if instructor reuses for demos).

### ★ Release Elastic IP

If you allocated an Elastic IP and attached it: **Release** after instance termination.

### Verify

```bash
aws ec2 describe-instances --query "Reservations[].Instances[?State.Name!='terminated'].InstanceId"
```

Should return `[]` or only instructor instances.

**Checkpoint ☐** My EC2 instances terminated  
**Checkpoint ☐** No unexpected running resources  

---

## Quick reference — commands

```bash
# Identity
aws sts get-caller-identity

# S3
aws s3 ls
aws s3 cp local.txt s3://bucket/
aws s3 ls s3://bucket/
aws s3 rm s3://bucket/local.txt

# EC2
aws ec2 describe-instances --output table

# SQS
aws sqs send-message --queue-url URL --message-body "test"
aws sqs receive-message --queue-url URL
aws sqs delete-queue --queue-url URL
```

---

## Linux cheat sheet (on EC2)

```bash
sudo systemctl status nginx
sudo systemctl restart nginx
curl http://localhost
ss -tlnp | grep :80
tail -f /var/log/nginx/access.log
```

---

## Report problems to instructor

| Symptom | Info to provide |
|---------|-----------------|
| AccessDenied | Command + screenshot of IAM user |
| SSH fail | Instance ID, public IP, SG inbound rules screenshot |
| Website not loading | Output of `curl localhost` on server + SG port 80 |

---

*Lab guide version 1.1 — AWS Club 4h workshop (Lab D SQS hands-on)*
