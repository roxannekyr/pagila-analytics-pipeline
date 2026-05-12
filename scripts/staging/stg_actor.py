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

project_id = 'project-401f4646-3663-4125-aaa' # project id
dataset_id = 'staging_db' # schema name: staging_db, reporting_db etc.
table_id = 'stg_actor' # table name: stg_customer, stg_city etc.

# # SQL Query

# Creating the BigQuery client
client = bigquery.Client(project=project_id)

query = """
with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.actor` --Your table path
  )

  , final as (
    select
        actor_id
        , first_name as actor_first_name
        , last_name as actor_last_name
        , last_update as actor_last_update
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
    bigquery.SchemaField('actor_id', 'INTEGER'),
    bigquery.SchemaField('actor_first_name', 'STRING'),
    bigquery.SchemaField('actor_last_name', 'STRING'),
    bigquery.SchemaField('actor_last_update', 'DATETIME'),
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

get_ipython().system('python3 -m jupyter nbconvert stg_actor.ipynb --to python')

get_ipython().system('python3 -m pip install nbconvert')

get_ipython().system('python3 -m pip install nbconvert -U')





