#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# # Import libraries

# In[1]:


# Importing libraries
from google.cloud import bigquery
import pandas as pd
from pandas_gbq import to_gbq
import os
import subprocess

print('Libraries imported successfully')


# In[2]:


# Setting the environment variable for Google Cloud credentials
# Placing the path in which the .json file is located.

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roxan\AppData\Roaming\gcloud\application_default_credentials.json"
# In[3]:


# Setting the Google Cloud project ID and BigQuery dataset details

project_id = 'project-401f4646-3663-4125-aaa' # project id
dataset_id = 'reporting_db' # schema name: staging_db, reporting_db etc.
table_id = 'rep_rentals_per_period' # table name: stg_customer, stg_city etc.

# # SQL Query

# In[4]:


# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query here
query = """ 
  with cte_rentals as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`

  )

  , cte_reporting_dates as (

      select * 
      from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
      where reporting_period in ('Day','Month','Year')

  )

  ,  cte_rentals_per_period as (

      select
          'Day' as reporting_period,
          date_trunc(rent.rental_rental_date,day) as reporting_date,
          count(*) as total_rentals
      from cte_rentals as rent
      group by reporting_period,reporting_date

      union all

      select
          'Month' as reporting_period,
          date_trunc(rent.rental_rental_date,month) as reporting_date,
          count(*) as total_rentals
      from cte_rentals as rent
      group by reporting_period,reporting_date

      union all

      select
          'Year' as reporting_period,
          date_trunc(rent.rental_rental_date,year) as reporting_date,
          count(*) as total_rentals
      from cte_rentals as rent
      group by reporting_period,reporting_date

  )
 -- All above combined with all dates master date table
 ,  cte_final as (

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_rentals_per_period.total_rentals,0) as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_rentals_per_period.total_rentals,0) as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_rentals_per_period.total_rentals,0) as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period 
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final;

"""

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

# # Writing to BigQuery

# In[5]:

# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Exploring some records
display(df.head())

# Defining table schema
schema = [
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('total_rentals', 'INTEGER')
]
# In[6]:

# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Checking if the table exists
def table_exists(client, full_table_id):
    try:
        client.get_table(full_table_id)
        return True
    except Exception:
        return False

# Writting the dataframe to the table (overwriting if it exists, creating if it doesn't)
if table_exists(client, full_table_id):
    # If the table exists, overwriting it
    destination_table = f"{dataset_id}.{table_id}"
    # Writting the dataframe to the table (overwriting if it exists)
    to_gbq(df, destination_table, project_id=project_id, if_exists='replace')
    print(f"Table {full_table_id} exists. Overwritten.")
else:
    # If the table does not exist, creating it
    job_config = bigquery.LoadJobConfig(schema=schema)
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Waitting for the job to complete
    print(f"Table {full_table_id} did not exist. Created and data loaded.")


# In[7]:


# Safely run terminal commands (replacing get_ipython)
try:
    subprocess.run(['python', '-m', 'pip', 'install', 'nbconvert', '-U'], check=True)
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_rentals_per_period.ipynb', '--to', 'python', '--output-dir=..'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")

