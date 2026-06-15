# Lab D — Amazon SQS

**Goal:** Decouple two EC2 instances with a message queue. **web1** publishes a counted message every 5 seconds; **web2** polls the queue and appends each message to a log file.

## Architecture

```
web1 (publisher)  ──send──▶  SQS queue  ──poll──▶  web2 (subscriber → sqs-messages.log)
```

## Files

| File | Runs on | Purpose |
|------|---------|---------|
| `publisher.py` | web1 | Sends JSON message every 5 s with incrementing `count` |
| `subscriber.py` | web2 | Long-polls queue, logs messages, deletes after processing |

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SQS_QUEUE_URL` | Yes | — | Full queue URL from the SQS console |
| `SQS_PUBLISH_INTERVAL` | No | `5` | Seconds between publisher messages |
| `SQS_LOG_FILE` | No | `/home/ec2-user/sqs-messages.log` | Subscriber output file |
| `SQS_WAIT_TIME` | No | `10` | Long-poll wait (seconds) |

## Quick checklist

1. **Create queue** — Standard queue `aws-club-<initials>-queue`
2. **Credentials on EC2** — `aws configure` on web1 and web2 (same lab user) **or** instance profile with SQS access
3. **Install boto3** — `sudo dnf install -y python3-boto3` on both instances
4. **Copy scripts** — `scp` both `.py` files to each instance (or only publisher → web1, subscriber → web2)
5. **Export queue URL** — `export SQS_QUEUE_URL='https://sqs...'`
6. **Run publisher on web1** — `python3 publisher.py`
7. **Run subscriber on web2** — `python3 subscriber.py` (separate SSH session)
8. **Verify** — `tail -f ~/sqs-messages.log` on web2 shows increasing `count` values
9. **Tear-down** — stop scripts (Ctrl+C), delete queue in SQS console
