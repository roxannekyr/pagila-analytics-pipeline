#!/bin/bash
set -e # Stops the execution if any script fails

export PATH=/usr/bin:$PATH

# Define your base directory once to keep things clean
BASE_DIR="/mnt/c/Users/roxan/Desktop/Personal/Learning & Development/2. IHU DATA ANALYTICS IN BUSINESS/Capstone/Capstone Roxani/Cron orchestration"

# Step into the directory first! This fixes 99% of Python path errors in Cron.
cd "$BASE_DIR"

# List all the reporting scripts you want to run in order
SCRIPTS=(
    "rep_customers_ordered.py"
    "rep_rentals_per_customer_and_period.py"
    "rep_rentals_per_period.py"
    "rep_revenue_per_customer_and_period.py"
)

echo "Starting Pagila reporting orchestration..."

# Loop through the list and run each one
for script in "${SCRIPTS[@]}"; do
    echo "▶ Running $script..."
    # Since we cd'd into the folder, we just call the script directly
    python3 "$script"
done

echo "✅ All reporting scripts completed successfully!"