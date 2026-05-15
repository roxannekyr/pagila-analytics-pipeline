#!/bin/bash
set -e
export PATH=/usr/bin:/usr/local/bin:$PATH
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/roxan/AppData/Roaming/gcloud/application_default_credentials.json"

BASE_DIR="/mnt/c/Users/roxan/Desktop/Personal/Learning & Development/2. IHU DATA ANALYTICS IN BUSINESS/Capstone/Capstone Roxani/Cron orchestration"
cd "$BASE_DIR"

PYTHON=$(which python3)

SCRIPTS=(
    "rep_customers_ordered.py"
    "rep_rentals_per_customer_and_period.py"
    "rep_rentals_per_period.py"
    "rep_revenue_per_customer_and_period.py"
    "rep_revenue_per_period.py"
    "rep_films_rented.py"
    "rep_rental_details.py"
)

echo "Starting Pagila reporting orchestration..."

for script in "${SCRIPTS[@]}"; do
    echo "▶ Running $script..."
    sed '/GOOGLE_APPLICATION_CREDENTIALS/d' "$script" \
        | sed 's/display(/print(/g' \
        | sed '/get_ipython/d' > "wsl_temp_script.py"
    $PYTHON "wsl_temp_script.py"
    rm "wsl_temp_script.py"
    echo "✅ $script completed."
done

echo "✅ All reporting scripts completed successfully!"