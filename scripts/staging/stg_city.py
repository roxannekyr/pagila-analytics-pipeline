#!/usr/bin/env python
# coding: utf-8

# # Import libraries

# In[ ]:


# Import libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')


# In[ ]:


# Set the environment variable for Google Cloud credentials
# Place the path in which the .json file is located.

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roxan\AppData\Roaming\gcloud\application_default_credentials.json"
# In[ ]:


# Set your Google Cloud project ID and BigQuery dataset details

project_id = 'project-401f4646-3663-4125-aaa' # Edit with your project id
dataset_id = 'staging_db' # Modify the necessary schema name: staging_db, reporting_db etc.
table_id = 'stg_city' # Modify the necessary table name: stg_customer, stg_city etc.

# # SQL Query

# In[ ]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Define your SQL query here
query = """
with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.city` --Your table path
  )

  , final as (
    select
          city_id
        , city as city_city
        , country_id as city_country_id
        , last_update as city_last_update
   FROM base
  )

  select * from final
"""

# Execute the query and store the result in a dataframe
df = client.query(query).to_dataframe()

# Explore some records
df.head()


# # Write to BigQuery

# In[ ]:


# Define the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Define table schema based on the project description

schema = [
    bigquery.SchemaField('city_id', 'INTEGER'),
    bigquery.SchemaField('city_city', 'STRING'),
    bigquery.SchemaField('city_country_id', 'INTEGER'),
    bigquery.SchemaField('city_last_update', 'DATETIME')
    ]
# In[ ]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Check if the table exists
def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

# Write the dataframe to the table (overwrite if it exists, create if it doesn't)
if table_exists(client, full_table_id):
    # If the table exists, overwrite it
    destination_table = f"{dataset_id}.{table_id}"
    # Write the dataframe to the table (overwrite if it exists)
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    # If the table does not exist, create it
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Table {full_table_id} did not exist. Created and data loaded.")


# In[ ]:


# Converting i.pynb file to .py python executable file.

get_ipython().system('python -m jupyter nbconvert stg_city.ipynb --to python')
# In[ ]:


get_ipython().system('python -m pip install nbconvert')


# In[ ]:


get_ipython().system('python -m pip install nbconvert -U')

