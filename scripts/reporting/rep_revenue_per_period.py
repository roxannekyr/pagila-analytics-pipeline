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
table_id = 'rep_revenue_per_period' # table name: stg_customer, stg_city etc.

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
      where reporting_period in ('Day','Month','Year') and reporting_date >= '2015-01-01'

  )

  /* Adding payment information to be able to calculate the revenue */
  , cte_payment as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`

  )

  /* Adding film information to be able to find the film title 'GOODFELLAS SALUTE' to filter out later in the where clause */
  , cte_film as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_film`

  )

  /* Adding inventory information. This table acts as a bridge table from where we can derive film's title data which will be used in the main 
  cte where we will calculate the revenue (& more specifically in the code section needed for the where clause limitation) */
  , cte_inventory as (

      select *
      from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
  )

  ,  cte_revenue_per_period as (

      select
          'Day' as reporting_period,
          CAST(date_trunc(rent.rental_rental_date, day) AS DATE) as reporting_date, -- Cast to DATE
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period, reporting_date

      union all

      select
          'Month' as reporting_period,
          CAST(date_trunc(rent.rental_rental_date, month) AS DATE) as reporting_date, -- Cast to DATE
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period, reporting_date

      union all

      select
          'Year' as reporting_period,
          CAST(date_trunc(rent.rental_rental_date, year) AS DATE) as reporting_date, -- Cast to DATE
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period, reporting_date

  )
 -- All above combined - final cte from where we see the result
 ,  cte_final as (

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_revenue_per_period.total_revenue,0) as total_revenue
      from cte_reporting_dates left join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_revenue_per_period.total_revenue,0) as total_revenue
      from cte_reporting_dates left join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          coalesce(cte_revenue_per_period.total_revenue,0) as total_revenue
      from cte_reporting_dates left join cte_revenue_per_period 
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final
  order by reporting_period ,reporting_date;

"""

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

# # Writing to BigQuery

# In[5]:

# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Data cleaning: ensuring the revenue is a float 
df['total_revenue'] = df['total_revenue'].astype('float64')

# Exploring some records
display(df.head())

# Defining table schema
schema = [
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('total_revenue', 'FLOAT')
]
# In[6]:

# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Configuring the load job to always overwrite if the table exists, or create if it doesn't
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE 
)

print(f"Loading data into {full_table_id}...")

# Running the job
job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
job.result()  # Wait for the job to complete

print(f"Data successfully loaded to {full_table_id}.")


# In[7]:


# Safely run terminal commands (replacing get_ipython)
try:
    subprocess.run(['python', '-m', 'pip', 'install', 'nbconvert', '-U'], check=True)
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_revenue_per_period.ipynb', '--to', 'python', '--output-dir=..'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")


# In[ ]:




