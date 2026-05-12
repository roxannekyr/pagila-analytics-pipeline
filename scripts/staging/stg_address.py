# Importing libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')

# Setting the environment variable for Google Cloud credentials
# Placing the path in which the .json file is located.

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roxan\AppData\Roaming\gcloud\application_default_credentials.json"

# Setting Google Cloud project ID and BigQuery dataset details

project_id = 'project-401f4646-3663-4125-aaa' # Edit with your project id
dataset_id = 'staging_db' # Modify the necessary schema name: staging_db, reporting_db etc.
table_id = 'stg_address' # Modify the necessary table name: stg_customer, stg_city etc.

# # SQL Query

# Creating the BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query 
query = """
with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.address` --Your table path
  )

  , final as (
    select
          address_id
        , address  as address_address
        , address2 as address_address2
        , district as address_district
        , city_id as address_city_id
        , postal_code as address_postal_code
        , phone as address_phone
        , last_update as address_last_update
   FROM base
  )

  select * from final
"""

# Executing the query and store the result in a dataframe
df = client.query(query).to_dataframe()

# Exploring some records
df.head()


# # Writing to BigQuery

# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Defining table schema based on the project description

schema = [
    bigquery.SchemaField('address_id', 'INTEGER'),
    bigquery.SchemaField('address_address', 'STRING'),
    bigquery.SchemaField('address_address2', 'STRING'),
    bigquery.SchemaField('address_district', 'STRING'),
    bigquery.SchemaField('address_city_id', 'INTEGER'),
    bigquery.SchemaField('address_postal_code', 'STRING'),
    bigquery.SchemaField('address_phone', 'STRING'),
    bigquery.SchemaField('address_last_update', 'DATETIME')
    ]

# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Checking if the table exists
def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

# Writing the dataframe to the table (overwriting if it exists, creating if it doesn't)
if table_exists(client, full_table_id):
    # If the table exists, overwriting it
    destination_table = f"{dataset_id}.{table_id}"
    # Writing the dataframe to the table (overwriting if it exists)
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    # If the table does not exist, creating it
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Waitting for the job to complete
    print(f"Table {full_table_id} did not exist. Created and data loaded.")

# Converting i.pynb file to .py python executable file.

get_ipython().system('python -m jupyter nbconvert stg_address.ipynb --to python')

get_ipython().system('python -m pip install nbconvert')

get_ipython().system('python -m pip install nbconvert -U')

