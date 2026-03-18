#!/bin/bash
# Create CDP Uploader SQS queues and S3 buckets for local development

echo "[INIT SCRIPT] Setting up CDP Uploader resources" >&2

echo "[INIT SCRIPT] Creating buckets" >&2
awslocal s3 mb s3://cdp-uploader-quarantine
awslocal s3 mb s3://my-bucket

echo "[INIT SCRIPT] Creating queues" >&2
awslocal sqs create-queue --queue-name cdp-clamav-results
awslocal sqs create-queue --queue-name cdp-uploader-scan-results-callback.fifo --attributes '{"FifoQueue":"true","ContentBasedDeduplication":"true"}'
awslocal sqs create-queue --queue-name cdp-uploader-download-requests --region eu-west-2

# Test harness (mock virus scanner)
awslocal sqs create-queue --queue-name mock-clamav
awslocal s3api put-bucket-notification-configuration \
  --bucket cdp-uploader-quarantine \
  --notification-configuration '{"QueueConfigurations":[{"QueueArn":"arn:aws:sqs:eu-west-2:000000000000:mock-clamav","Events":["s3:ObjectCreated:*"]}]}'