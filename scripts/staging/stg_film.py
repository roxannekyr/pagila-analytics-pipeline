#!/usr/bin/env python
# coding: utf-8

# # Import libraries

# In[1]:


# Import libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os

print('Libraries imported successfully')


# In[2]:


# Set the environment variable for Google Cloud credentials
# Place the path in which the .json file is located.

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roxan\AppData\Roaming\gcloud\application_default_credentials.json"


# In[3]:


# Set your Google Cloud project ID and BigQuery dataset details

project_id = 'project-401f4646-3663-4125-aaa' # Edit with your project id
dataset_id = 'staging_db' # Modify the necessary schema name: staging_db, reporting_db etc.
table_id = 'stg_film' # Modify the necessary table name: stg_customer, stg_city etc.


# # SQL Query

# In[4]:


# Create a BigQuery client
client = bigquery.Client(project=project_id)

# Define your SQL query here
query = """
with base as (
  select *
  from `project-401f4646-3663-4125-aaa.pagila_productionpublic.film` 
  )

  , final as (
    select
          film_id
        , title as film_title
        , description as film_description
        , language_id as film_language_id
        , original_language_id as film_original_language_id
        , rental_duration as film_rental_duration
        , rental_rate as film_rental_rate
        , length as film_length
        , replacement_cost as film_replacement_cost
        , rating as film_rating
        , last_update as film_last_update
        , special_features as film_special_features
        , fulltext as film_fulltext
   FROM base
  )

  select * from final
"""

# Execute the query and store the result in a dataframe
df = client.query(query).to_dataframe()

# Explore some records
df.head()


# # Write to BigQuery

# In[5]:


# Define the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Define table schema based on the project description

schema = [
    bigquery.SchemaField('film_id', 'INTEGER'),
    bigquery.SchemaField('film_title', 'STRING'),
    bigquery.SchemaField('film_description', 'STRING'),
    bigquery.SchemaField('film_language_id', 'INTEGER'),
    bigquery.SchemaField('film_original_language_id', 'INTEGER'),
    bigquery.SchemaField('film_rental_duration', 'INTEGER'),
    bigquery.SchemaField('film_rental_rate', 'FLOAT'),
    bigquery.SchemaField('film_length', 'INTEGER'),
    bigquery.SchemaField('film_replacement_cost', 'FLOAT'),
    bigquery.SchemaField('film_rating', 'STRING'),
    bigquery.SchemaField('film_last_update', 'DATETIME'),
    bigquery.SchemaField('film_special_features', 'STRING'),
    bigquery.SchemaField('film_fulltext', 'STRING'),
    ]


# In[6]:


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

get_ipython().system("python -m jupyter nbconvert stg_film.ipynb --to python --output-dir='../'")


# In[ ]:


get_ipython().system('python -m pip install nbconvert')


# In[ ]:


get_ipython().system('python -m pip install nbconvert -U')

