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
table_id = 'rep_customers_ordered' # table name: stg_customer, stg_city etc.

# # SQL Query

# In[4]:


# Creating a BigQuery client
client = bigquery.Client(project=project_id)

# Defining the SQL query here
query = """


    with cte_customers as (
        select *
        from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
    )
    , cte_rentals as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`
    )

    /* Calculating customer_lifespan */
    , cte_customer_lifespan as (
        select
            rent.rental_customer_id as customer_id,
            date(min(rent.rental_rental_date)) as first_rent,
            date(max(rent.rental_rental_date)) as last_rent,
            date_diff(DATE(max(rent.rental_rental_date)), DATE(min(rent.rental_rental_date)), month) as customer_lifespan 
        from cte_rentals as rent
        group by rent.rental_customer_id
    )

    /* Calculating customer recency */
    , cte_customer_recency as (
        select
        rent.rental_customer_id as customer_id,date_diff((select date(max(rental_rental_date)) from cte_rentals),date(max(rental_rental_date)),month
        ) as recency
    from cte_rentals as rent
    group by rent.rental_customer_id
    )

    , cte_payment as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`
    )

    , cte_film as (
        select * 
        from `project-401f4646-3663-4125-aaa.staging_db.stg_film`
    )

    , cte_inventory as (
        select *
        from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
    )

    , cte_address as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_address`
    )

    , cte_city as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_city`
    )

    , cte_country as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_country`
    )


    /* Lifetime totals per customer */
    , cte_lifetime_revenue as (
        select
            cte_country.country as country,
            cte_city.city_city as city,
            cte_customers.customer_id,
            concat(cte_customers.customer_first_name, ' ', cte_customers.customer_last_name) as customer_name,
            1 as total_customers_ordered,
            count(distinct rent.rental_id) as total_unique_orders,
            count(distinct film.film_id) as total_films_rented,
            sum(payment.payment_amount) as total_revenue
        from cte_rentals as rent
        left join cte_payment as payment
            on rent.rental_id = payment.payment_rental_id
                left join cte_inventory as inv
                    on rent.rental_inventory_id = inv.inventory_id
                        left join cte_film as film
                            on inv.inventory_film_id = film.film_id
                                left join cte_customers
                                    on rent.rental_customer_id = cte_customers.customer_id
                                        left join cte_address
                                            on cte_customers.customer_address_id=cte_address.address_id
                                                left join cte_city
                                                    on cte_address.address_city_id=cte_city.city_id
                                                        left join cte_country
                                                            on cte_city.city_country_id=cte_country.country_id

        where film.film_title not in ('GOODFELLAS SALUTE')
        group by cte_customers.customer_id, customer_name,city,country
    )

    , cte_final as (
        select
        cte_lifetime_revenue.country,
        cte_lifetime_revenue.city,
        cte_lifetime_revenue.customer_id,
        cte_lifetime_revenue.customer_name,
        cte_customer_lifespan.first_rent,
        cte_customer_lifespan.last_rent,
        case when cte_customer_lifespan.customer_lifespan >= 10 then 'Loyal'
            when cte_customer_lifespan.customer_lifespan >= 4  then 'Regular'
            else 'New'
        end as customer_segment,
        cte_customer_recency.recency,
        total_customers_ordered,
        cte_lifetime_revenue.total_unique_orders,
        cte_lifetime_revenue.total_films_rented,
        cte_lifetime_revenue.total_revenue,
        cte_lifetime_revenue.total_revenue / nullif(cte_lifetime_revenue.total_unique_orders, 0) as average_rental_value,
        case when cte_customer_lifespan.customer_lifespan = 0 then cte_lifetime_revenue.total_revenue
            else cte_lifetime_revenue.total_revenue / cte_customer_lifespan.customer_lifespan
        end as average_monthly_revenue
    from cte_lifetime_revenue
    inner join cte_customer_lifespan
        on cte_lifetime_revenue.customer_id = cte_customer_lifespan.customer_id
            inner join cte_customer_recency
                on cte_lifetime_revenue.customer_id = cte_customer_recency.customer_id
    )

    select * from cte_final
    order by customer_id

    /* Checking totals */

    /*
    -----------------------------------------------------------------------------------------------------
    PS: One row per customer showing lifetime metrics, segment, and recency.
        Used as a dimension table in Tableau, related to rep_rental_details via customer_id.
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
df['average_rental_value'] = df['average_rental_value'].astype('float64')
df['average_monthly_revenue'] = df['average_monthly_revenue'].astype('float64')

# Exploring some records
print(df.head())

# Defining table schema based on the project description

schema = [
    bigquery.SchemaField('country','STRING'),
    bigquery.SchemaField('city','STRING'),
    bigquery.SchemaField('customer_id','INTEGER'),
    bigquery.SchemaField('customer_name','STRING'),
    bigquery.SchemaField('first_rent','DATE'),
    bigquery.SchemaField('last_rent','DATE'),
    bigquery.SchemaField('customer_segment','STRING'),
    bigquery.SchemaField('recency','INTEGER'),
    bigquery.SchemaField('total_customers_ordered','INTEGER'),
    bigquery.SchemaField('total_unique_orders', 'INTEGER'),
    bigquery.SchemaField('total_films_rented','INTEGER'),
    bigquery.SchemaField('total_revenue','FLOAT64'),
    bigquery.SchemaField('average_rental_value','FLOAT64'),
    bigquery.SchemaField('average_monthly_revenue','FLOAT64'),
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
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_customers_ordered.ipynb', '--to', 'python','--output-dir=../python/reporting'], check=True)  # fixed path
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")

