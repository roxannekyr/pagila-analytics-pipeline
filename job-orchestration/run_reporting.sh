#!/bin/bash
set -e # Stops the execution if any script fails

export PATH=/usr/bin:$PATH
# This handles the Linux credentials globally
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/roxan/AppData/Roaming/gcloud/application_default_credentials.json"

BASE_DIR="/mnt/c/Users/roxan/Desktop/Personal/Learning & Development/2. IHU DATA ANALYTICS IN BUSINESS/Capstone/Capstone Roxani/Cron orchestration"
cd "$BASE_DIR"

SCRIPTS=(
    "rep_customers_ordered.py"
    "rep_rentals_per_customer_and_period.py"
    "rep_rentals_per_period.py"
    "rep_revenue_per_customer_and_period.py"
    "rep_revenue_per_period.py"
    "rep_films_rented.py"
)

echo "Starting Pagila reporting orchestration..."

for script in "${SCRIPTS[@]}"; do
    echo "▶ Running $script..."
    
    # 1. Copy the script to a temporary file, deleting the hardcoded Windows path line
    sed '/GOOGLE_APPLICATION_CREDENTIALS/d' "$script" > "wsl_temp_script.py"
    
    # 2. Run the temporary, Linux-friendly version
    python3 "wsl_temp_script.py"
    
    # 3. Clean up the temp file so your directory stays tidy
    rm "wsl_temp_script.py"
done

echo "✅ All reporting scripts completed successfully!"