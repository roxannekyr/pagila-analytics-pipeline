#!/bin/bash
set -e
export PATH=/usr/bin:/usr/local/bin:$PATH
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/roxan/AppData/Roaming/gcloud/application_default_credentials.json"

BASE_DIR="/mnt/c/Users/roxan/Desktop/Personal/Learning & Development/2. IHU DATA ANALYTICS IN BUSINESS/Capstone/Capstone Roxani/Cron orchestration"
cd "$BASE_DIR"

PYTHON=$(which python3)

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

    # Strip Windows credentials line, replace display() with print(), remove get_ipython() lines
    sed '/GOOGLE_APPLICATION_CREDENTIALS/d' "$script" \
        | sed 's/display(/print(/g' \
        | sed '/get_ipython/d' > "wsl_temp_script.py"

    # Run the temporary, Linux-friendly version
    $PYTHON "wsl_temp_script.py"

    # Clean up
    rm "wsl_temp_script.py"

    echo "✅ $script completed."
done

echo "✅ All staging scripts completed successfully!"