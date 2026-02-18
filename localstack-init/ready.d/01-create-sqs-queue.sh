#!/bin/bash
# Create SQS queue for ai-defra-search-agent chat worker
# Queue name must match SQS_CHAT_QUEUE_URL in .env
awslocal sqs create-queue --queue-name ai-defra-search-agent-invoke
