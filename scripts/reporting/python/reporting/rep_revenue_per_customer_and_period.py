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
table_id = 'rep_revenue_per_customer_and_period' # table name: stg_customer, stg_city etc.

# # SQL Query

# In[4]:


# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query here
query = """


  with cte_rentals as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
  )

  ,cte_reporting_dates as (
    select *
    from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
    where reporting_period in ('Day','Month','Year')
      and reporting_date >= '2015-01-01'
  )

  ,cte_customers as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
  )

  ,cte_payment as (
  select * from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`   
  )

  ,cte_film as (
  select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film`   
  )

  ,cte_inventory as (
  select * from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory` 
  )

  ,cte_revenue_per_period as (
      select
          'Day' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), day) as reporting_date,   -- if timestamp now aggregated in daily level
          cte_customers.customer_id,
          sum(payment_amount) as total_revenue
      from cte_rentals as rentals left join cte_payment as payment 
        on rentals.rental_id = payment.payment_rental_id
          left join cte_inventory as inventory
            on rentals.rental_inventory_id = inventory.inventory_id
              left join cte_film as film    
                on inventory.inventory_film_id = film.film_id
                  left join cte_customers 
                    on rentals.rental_customer_id=cte_customers.customer_id
      where film.film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period,reporting_date,cte_customers.customer_id

      union all

      select
          'Month' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), month) as reporting_date,   -- if timestamp now aggregated in monthly level
          cte_customers.customer_id,
          sum(payment_amount) as total_revenue
      from cte_rentals as rentals left join cte_payment as payment 
        on rentals.rental_id = payment.payment_rental_id
          left join cte_inventory as inventory
            on rentals.rental_inventory_id = inventory.inventory_id
              left join cte_film as film    
                on inventory.inventory_film_id = film.film_id
                  left join cte_customers 
                    on rentals.rental_customer_id=cte_customers.customer_id
      where film.film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period,reporting_date,cte_customers.customer_id

      union all

      select
          'Year' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), year) as reporting_date,   -- if timestamp now aggregated in yearly level
          cte_customers.customer_id,
          sum(payment_amount) as total_revenue
      from cte_rentals as rentals left join cte_payment as payment 
        on rentals.rental_id = payment.payment_rental_id
          left join cte_inventory as inventory
            on rentals.rental_inventory_id = inventory.inventory_id
              left join cte_film as film    
                on inventory.inventory_film_id = film.film_id
                  left join cte_customers 
                    on rentals.rental_customer_id=cte_customers.customer_id
      where film.film_title not in ('GOODFELLAS SALUTE')
      group by reporting_period,reporting_date,cte_customers.customer_id

  )

 ,  cte_final as (

      select
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.customer_id,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date
        inner join cte_customers 
            on cte_revenue_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Day'

      union all
      select
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.customer_id,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date
        inner join cte_customers 
            on cte_revenue_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Month'

      union all
      select
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.customer_id,
          cte_revenue_per_period.total_revenue as total_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date
        inner join cte_customers 
            on cte_revenue_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Year'
 )

  select * from cte_final
  order by total_revenue desc

  /* Checking totals */

  /*
    select 
        sum(total_revenue) as total_revenue
    from cte_final
    where reporting_period = 'Day'; 

    */

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
print(df.head())

# Defining table schema
schema = [
    bigquery.SchemaField('customer_id', 'INTEGER'),
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('total_revenue', 'FLOAT')
]

# In[6]:

# Configure the load job to ALWAYS overwrite if the table exists, or create if it doesn't
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)

print(f"Loading data into {full_table_id}...")

# Run the job
job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
job.result()  # Wait for the job to complete

print(f"Data successfully loaded to {full_table_id}.")

# In[7]:

# Safely running terminal commands
try:
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_revenue_per_customer_and_period.ipynb','--to', 'python','--output-dir=../python/reporting'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")

