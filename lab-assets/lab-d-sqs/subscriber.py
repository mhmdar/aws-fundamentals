#!/usr/bin/env python3
"""AWS Club Lab D — SQS subscriber (run on web2)."""

import json
import os
import time
from datetime import datetime, timezone

import boto3

QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
LOG_FILE = os.environ.get("SQS_LOG_FILE", "/home/ec2-user/sqs-messages.log")
WAIT_TIME = int(os.environ.get("SQS_WAIT_TIME", "10"))


def main() -> None:
    if not QUEUE_URL:
        raise SystemExit("Set SQS_QUEUE_URL to your queue URL")

    sqs = boto3.client("sqs")
    print(f"Subscribing to {QUEUE_URL}, logging to {LOG_FILE}")

    while True:
        resp = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=WAIT_TIME,
        )
        messages = resp.get("Messages", [])
        if not messages:
            continue

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for msg in messages:
                ts = datetime.now(timezone.utc).isoformat()
                body = msg["Body"]
                try:
                    parsed = json.loads(body)
                    line = (
                        f"{ts} count={parsed.get('count')} "
                        f"hostname={parsed.get('hostname')} body={body}\n"
                    )
                except json.JSONDecodeError:
                    line = f"{ts} body={body}\n"
                f.write(line)
                f.flush()
                print(line.rstrip())
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"],
                )


if __name__ == "__main__":
    main()
