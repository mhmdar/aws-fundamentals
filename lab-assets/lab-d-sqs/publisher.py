#!/usr/bin/env python3
"""AWS Club Lab D — SQS publisher (run on web1)."""

import json
import os
import socket
import time

import boto3

QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
INTERVAL = int(os.environ.get("SQS_PUBLISH_INTERVAL", "5"))


def main() -> None:
    if not QUEUE_URL:
        raise SystemExit("Set SQS_QUEUE_URL to your queue URL")

    sqs = boto3.client("sqs")
    count = 0
    hostname = socket.gethostname()

    print(f"Publishing to {QUEUE_URL} every {INTERVAL}s from {hostname}")

    while True:
        count += 1
        body = json.dumps(
            {
                "count": count,
                "hostname": hostname,
                "message": f"Hello from AWS Club lab — message #{count}",
            }
        )
        resp = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=body)
        print(f"Sent #{count} MessageId={resp['MessageId']}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
