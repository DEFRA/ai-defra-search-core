#!/bin/bash
# Create S3 buckets for local development
awslocal s3 mb s3://ai-defra-search-knowledge-upload-local
awslocal s3 mb s3://test-results  # perf-tests JMeter output
