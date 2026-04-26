#!/usr/bin/env bash

BUCKET_NAME=pulumi-data

aws --profile rustfs \
  --endpoint-url http://localhost:9000 \
  s3 mb s3://${BUCKET_NAME}

aws --profile rustfs \
  --endpoint-url http://localhost:9000 \
  s3 ls s3://