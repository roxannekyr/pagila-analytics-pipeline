#!/bin/bash
set -e
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/roxan/AppData/Roaming/gcloud/application_default_credentials.json"

# Define your base directory
BASE_DIR="/mnt/c/Users/roxan/Desktop/Personal/Learning & Development/2. IHU DATA ANALYTICS IN BUSINESS/Capstone/Capstone Roxani/Cron orchestration"

# Step into the directory first! This fixes 99% of Python path errors in Cron.
cd "$BASE_DIR"

SCRIPTS=(
    "stg_actor.py"
    "stg_address.py"
    "stg_category.py"
    "stg_city.py"
    "stg_country.py"
    "stg_customer.py"
    "stg_film_actor.py"
    "stg_film_category.py"
    "stg_film.py"
    "stg_inventory.py"
    "stg_language.py"
    "stg_payment.py"
    "stg_rental.py"
    "stg_staff.py"
    "stg_store.py"
)

echo "Starting Pagila staging orchestration..."

for script in "${SCRIPTS[@]}"; do
    echo "▶ Running $script..."
    # Since we cd'd into the folder, we just call the script directly
    python3 "$script"
done

echo "✅ All staging scripts completed successfully!"
