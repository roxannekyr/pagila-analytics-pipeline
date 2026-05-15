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
table_id = 'rep_films_rented' # table name: stg_customer, stg_city etc.

# # SQL Query

# In[4]:

# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query here
query = """

/* Base query is the film information */

with cte_rentals as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
)
, cte_inventory as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
)
, cte_film as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
)
, cte_film_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_film_category`
)
, cte_category as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_category`
)
, cte_payment as (
    select * from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
)

/* Calculating film_lifespan */
, cte_film_lifespan as (
    select
        inv.inventory_film_id as film_id,
        cast(min(rent.rental_rental_date) as date) as first_rent,
        cast(max(rent.rental_rental_date) as date) as last_rent,
        date_diff(cast(max(rent.rental_rental_date) as date),
                  cast(min(rent.rental_rental_date) as date), month) as film_lifespan
    from cte_rentals as rent
    inner join cte_inventory as inv
        on rent.rental_inventory_id = inv.inventory_id
    group by inv.inventory_film_id
)

/* Lifetime totals per film */
, cte_lifetime_revenue as (
    select
        category.category_id,
        category.category_name,
        film.film_id,
        film.film_title,
        count(distinct rent.rental_id) as total_unique_orders,
        sum(payment.payment_amount) as total_revenue
    from cte_rentals as rent
    left join cte_payment as payment
        on rent.rental_id = payment.payment_rental_id
            left join cte_inventory as inv
                on rent.rental_inventory_id = inv.inventory_id
                    left join cte_film as film
                        on inv.inventory_film_id = film.film_id
                            left join cte_film_category as film_category
                                on film.film_id = film_category.film_category_film_id
                                    left join cte_category as category
                                        on film_category.film_category_category_id = category.category_id
    where film.film_title not in ('GOODFELLAS SALUTE')
    group by category.category_id, category.category_name, film.film_id, film.film_title
)

select
    cte_lifetime_revenue.category_id,
    cte_lifetime_revenue.category_name,
    cte_lifetime_revenue.film_id,
    cte_lifetime_revenue.film_title,
    cte_film_lifespan.first_rent,
    cte_film_lifespan.last_rent,
    case when cte_film_lifespan.film_lifespan >= 12 then 'High-Performer'
         when cte_film_lifespan.film_lifespan >= 6  then 'Mid-Performer'
         else 'New'
    end as product_segment,
    cte_lifetime_revenue.total_unique_orders,
    cte_lifetime_revenue.total_revenue,
    round(cte_lifetime_revenue.total_revenue / nullif(cte_lifetime_revenue.total_unique_orders, 0), 2) as avg_order_revenue,
    case when cte_film_lifespan.film_lifespan = 0 then cte_lifetime_revenue.total_revenue
         else round(cte_lifetime_revenue.total_revenue / cte_film_lifespan.film_lifespan, 2)
    end as avg_monthly_revenue
from cte_lifetime_revenue
inner join cte_film_lifespan
    on cte_lifetime_revenue.film_id = cte_film_lifespan.film_id

order by cte_lifetime_revenue.film_id;

/*
-----------------------------------------------------------------------------------------------------
PS: One row per film showing lifetime metrics, product segment, and category.
    Used as a dimension table in Tableau, related to rep_rental_details via film_id.
-----------------------------------------------------------------------------------------------------
*/

"""

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

# # Writing to BigQuery

# In[5]:


# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

df['total_revenue'] = df['total_revenue'].astype('float64')
df['avg_order_revenue'] = df['avg_order_revenue'].astype('float64')
df['avg_monthly_revenue'] = df['avg_monthly_revenue'].astype('float64')

# Exploring some records
print(df.head())

# Defining table schema based on the project description

schema = [
    bigquery.SchemaField('category_id','INTEGER'),
    bigquery.SchemaField('category_name','STRING'),
    bigquery.SchemaField('film_id','INTEGER'),
    bigquery.SchemaField('film_title','STRING'),
    bigquery.SchemaField('first_rent','DATE'),
    bigquery.SchemaField('last_rent','DATE'),
    bigquery.SchemaField('product_segment','STRING'),
    bigquery.SchemaField('total_unique_orders','INTEGER'),
    bigquery.SchemaField('total_revenue','FLOAT64'),
    bigquery.SchemaField('avg_order_revenue','FLOAT64'),
    bigquery.SchemaField('avg_monthly_revenue','FLOAT64'),
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
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_films_rented.ipynb', '--to', 'python', '--output-dir=..'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")

