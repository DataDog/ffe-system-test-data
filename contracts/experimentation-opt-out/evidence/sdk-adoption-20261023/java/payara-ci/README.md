# Payara build failure at 578ffa77

The hosted job failed because Maven Central returned HTTP 429 Too Many Requests.
All three existing attempts failed while downloading the Spring Boot 2.6.0 parent POM.
The failure occurs at Dockerfile line 10, before the candidate agent is copied or installed.
The application did not build or run.

The workflow is unchanged from merged master. This is an external dependency rate limit.
The evidence does not demonstrate an opt-out regression or a simultaneous failure on master.
No source change or CI retry was made. The hosted job remains failed.

`failure-receipt.json` records the exact head, job, attempts, and raw log hashes.
`job-log-excerpt.txt` preserves the actual error from each attempt.
`source-binding.json` binds the workflow comparison and exact system-tests Dockerfile.
