#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
table_id = 'rep_rental_details' # table name: stg_customer, stg_city etc.

# # SQL Query

# In[4]:


# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query here
query = """

    /*Base query is the rentals*/
    with cte_rentals as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
    )

    ,   cte_customers as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
    )

    ,cte_inventory as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
    )

    ,cte_film as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
    )   

    ,cte_film_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film_category`
    )

    ,cte_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_category`
    )
    ,cte_payment as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
    )

select

    rental.rental_id,
    cast(rental.rental_rental_date as date) as rental_date,
    customer.customer_id,
    concat(customer.customer_first_name, ' ', customer.customer_last_name) as customer_name,
    film.film_id,
    film.film_title,
    category.category_id,
    category.category_name,
    coalesce(payment.payment_amount,0) as total_revenue

from cte_rentals as rental
left join cte_payment as payment  
    on rental.rental_id=payment.payment_rental_id
        left join cte_inventory as inventory  
            on rental.rental_inventory_id=inventory.inventory_id
                left join cte_film as film 
                    on inventory.inventory_film_id=film.film_id
                        left join cte_film_category as film_category 
                            on film.film_id=film_category.film_category_film_id
                                left join cte_category as category  
                                    on film_category.film_category_category_id=category.category_id
                                        left join cte_customers as customer 
                                            on rental.rental_customer_id=customer.customer_id

where film.film_title not in ('GOODFELLAS SALUTE')

order by rental.rental_rental_date desc, rental.rental_id;

/* 
---------------------------------------------------------------------------------------------------------------------------
PS: This is a rental fact table where one row per rental transaction that includes both film id & customer id
---------------------------------------------------------------------------------------------------------------------------
*/

"""

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

# # Writing to BigQuery

# In[5]:


# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

df['total_revenue'] = df['total_revenue'].astype('float64')

# Exploring some records
print(df.head())

# Defining table schema based on the project description

schema = [
    bigquery.SchemaField('rental_id',      'INTEGER'),
    bigquery.SchemaField('rental_date',    'DATE'),
    bigquery.SchemaField('customer_id',    'INTEGER'),
    bigquery.SchemaField('customer_name',  'STRING'),
    bigquery.SchemaField('film_id',        'INTEGER'),
    bigquery.SchemaField('film_title',     'STRING'),
    bigquery.SchemaField('category_id',    'INTEGER'),
    bigquery.SchemaField('category_name',  'STRING'),
    bigquery.SchemaField('total_revenue',  'FLOAT64'),
]

# In[6]:

# Configuring the load job to always overwrite if the table exists, or creating if it doesn't
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

# Safely running terminal commands 
try:
    subprocess.run(['python', '-m', 'pip', 'install', 'nbconvert', '-U'], check=True)
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_rental_details.ipynb', '--to', 'python', '--output-dir=../../python/reporting'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")

