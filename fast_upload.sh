#!/bin/bash
# Fast Upload Script with 1000 rows per batch
# This script runs the batch upload with a much larger batch size to speed up the process.

# Set environment variables
export SUPABASE_URL="https://nrtaztkewvbtzhbtkffc.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ydGF6dGtld3ZidHpoYnRrZmZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDI1NjM3NSwiZXhwIjoyMDY5ODMyMzc1fQ.qJas9ux_U-1V4lbx3XuIeEOIEx68so9kXbwRN7w5gXU"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ydGF6dGtld3ZidHpoYnRrZmZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyNTYzNzUsImV4cCI6MjA2OTgzMjM3NX0.vW4SpQRHuUppUbTcbgpTOjqE6lQMmPBl7E6uEIgd1z4"

# Run the batch upload in the background with a much larger batch size
nohup python batch_upload.py --batch-size 1000 --delay-seconds 3 > upload_log_fast.txt 2>&1 &

# Get the process ID
PID=$!

echo "Fast upload process started with PID: $PID"
echo "Using batch size: 1000 rows per batch"
echo "You can check the progress with: tail -f upload_log_fast.txt"
echo "You can stop the process with: kill $PID"

