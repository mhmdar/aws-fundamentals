# Lab C — Application Load Balancer

**Goal:** Launch a second EC2 web server, then put both instances behind an **Application Load Balancer** (ALB). With stickiness **disabled**, refreshing the ALB URL shows a different **hostname** / private IP — proof that traffic is split across machines.

## Shared assets (from Lab B)

| File | Purpose |
|------|---------|
| `../lab-b-ec2/index.html` | Welcome page — deploy **identical copy** to web1 and web2 |
| `../lab-b-ec2/nginx-lab-snippet.conf` | `sub_filter` lines → `/etc/nginx/default.d/aws-club-lab.conf` (AL2023) |

## Quick checklist

1. **Second public subnet** in another AZ (`10.0.2.0/24`) — ALB requires subnets in ≥2 AZs
2. **Launch `aws-club-<initials>-web2`** — same AMI, SG, nginx setup as web1
3. **Target group** — HTTP :80, health check `/`, register both instances, **stickiness off**
4. **ALB** — EC2 console → Load Balancers → **Application Load Balancer**, internet-facing, HTTP :80 → target group
5. **Test** — open `http://<alb-dns>/`, refresh 5–10 times; hostname alternates between instances
6. **Stretch** — `sudo systemctl stop nginx` on one instance → target unhealthy → only one hostname appears

## Tear-down (in addition to Lab B)

- Delete load balancer
- Delete target group
- Terminate web2, then web1
- Delete VPC resources (IGW, subnets, route tables, VPC)
