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
/* Base query is the customer information */
  with cte_customers as (

      select *
      from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`
  )

  , cte_rentals as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`

  )

  , cte_reporting_dates as (

      select * 
      from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
      where reporting_period in ('Day','Month','Year') and reporting_date >= '2015-01-01'

  )

  /* Calculating customer_lifespan */
  , cte_customer_lifespan as (
      select
          rent.rental_customer_id as customer_id,
          date(min(rent.rental_rental_date)) as first_rent,
          date(max(rent.rental_rental_date)) as last_rent,
          date_diff(max(rent.rental_rental_date), min(rent.rental_rental_date), month) as customer_lifespan
      from cte_rentals as rent
      group by rent.rental_customer_id

  )

  /* Calculating customer recency */
  , cte_customer_recency as (
    select 
      rent.rental_customer_id as customer_id,
      date_diff(current_date(), date(max(rental_rental_date)), month) as recency
    from cte_rentals as rent
    group by rent.rental_customer_id

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

  /* Added a left join to table customers to be able to view here data regarding customers & selected to view also customer_id column, while also 
     added in the group by clause also the customer id to be able to see data per reporting period per reporting date and per customer */
  ,  cte_revenue_per_period as (

      select
          cte_customers.customer_id,
          concat(cte_customers.customer_first_name, ' ',cte_customers.customer_last_name) as customer_name,
          'Day' as reporting_period,
          date_trunc(rent.rental_rental_date,day) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          count(distinct film.film_id) as total_films_rented,
          sum(payment_amount) as total_revenue

      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,customer_name,reporting_period,reporting_date

      union all

      select
          cte_customers.customer_id,
          concat(cte_customers.customer_first_name, ' ',cte_customers.customer_last_name) as customer_name,
          'Month' as reporting_period,
          date_trunc(rent.rental_rental_date,month) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          count(distinct film.film_id) as total_films_rented,
          sum(payment_amount) as total_revenue

      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,customer_name,reporting_period,reporting_date

      union all

      select
          cte_customers.customer_id,
          concat(cte_customers.customer_first_name, ' ',cte_customers.customer_last_name) as customer_name,
          'Year' as reporting_period,
          date_trunc(rent.rental_rental_date,year) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          count(distinct film.film_id) as total_films_rented,
          sum(payment_amount) as total_revenue

      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_customers 
                    on rent.rental_customer_id=cte_customers.customer_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by cte_customers.customer_id,customer_name,reporting_period,reporting_date

  )
 -- All above combined - final cte from where we see the result
 ,  cte_final as (

      select
          cte_revenue_per_period.customer_id, 
          cte_revenue_per_period.customer_name,
          cte_customer_lifespan.first_rent,
          cte_customer_lifespan.last_rent,
      --  cte_customer_lifespan.customer_lifespan,
          case when cte_customer_lifespan.customer_lifespan >= 12 then 'Loyal'
					     when cte_customer_lifespan.customer_lifespan >= 6 then 'Regular'
					     else 'New'
				  end as customer_segment,
          cte_customer_recency.recency,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_unique_orders as total_unique_orders,
          cte_revenue_per_period.total_films_rented as total_films_rented,
          cte_revenue_per_period.total_revenue as total_revenue,
          cte_revenue_per_period.total_revenue/nullif(cte_revenue_per_period.total_unique_orders,0) as average_rentals_value,
          case when cte_customer_lifespan.customer_lifespan = 0 then cte_revenue_per_period.total_revenue                            
					     else cte_revenue_per_period.total_revenue/ cte_customer_lifespan.customer_lifespan
				  end as average_monthly_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on (cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date)
          inner join cte_customer_lifespan 
            on cte_revenue_per_period.customer_id = cte_customer_lifespan.customer_id
              inner join cte_customer_recency
                on cte_revenue_per_period.customer_id = cte_customer_recency.customer_id
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select
          cte_revenue_per_period.customer_id, 
          cte_revenue_per_period.customer_name,
          cte_customer_lifespan.first_rent,
          cte_customer_lifespan.last_rent,
      --  cte_customer_lifespan.customer_lifespan,
          case when cte_customer_lifespan.customer_lifespan >= 12 then 'Loyal'
					     when cte_customer_lifespan.customer_lifespan >= 6 then 'Regular'
					     else 'New'
				  end as customer_segment,
          cte_customer_recency.recency,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_unique_orders as total_unique_orders,
          cte_revenue_per_period.total_films_rented as total_films_rented,
          cte_revenue_per_period.total_revenue as total_revenue,
          cte_revenue_per_period.total_revenue/nullif(cte_revenue_per_period.total_unique_orders,0) as average_rentals_value,
          case when cte_customer_lifespan.customer_lifespan = 0 then cte_revenue_per_period.total_revenue                            
					     else cte_revenue_per_period.total_revenue/ cte_customer_lifespan.customer_lifespan
				  end as average_monthly_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on (cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date)
          inner join cte_customer_lifespan 
            on cte_revenue_per_period.customer_id = cte_customer_lifespan.customer_id
              inner join cte_customer_recency
                on cte_revenue_per_period.customer_id = cte_customer_recency.customer_id
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select
          cte_revenue_per_period.customer_id, 
          cte_revenue_per_period.customer_name,
          cte_customer_lifespan.first_rent,
          cte_customer_lifespan.last_rent,
      --  cte_customer_lifespan.customer_lifespan,
          case when cte_customer_lifespan.customer_lifespan >= 12 then 'Loyal'
					     when cte_customer_lifespan.customer_lifespan >= 6 then 'Regular'
					     else 'New'
				  end as customer_segment,
          cte_customer_recency.recency,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_unique_orders as total_unique_orders,
          cte_revenue_per_period.total_films_rented as total_films_rented,
          cte_revenue_per_period.total_revenue as total_revenue,
          cte_revenue_per_period.total_revenue/nullif(cte_revenue_per_period.total_unique_orders,0) as average_rentals_value,
          case when cte_customer_lifespan.customer_lifespan = 0 then cte_revenue_per_period.total_revenue                            
					     else cte_revenue_per_period.total_revenue/ cte_customer_lifespan.customer_lifespan
				  end as average_monthly_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on (cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date)
          inner join cte_customer_lifespan 
            on cte_revenue_per_period.customer_id = cte_customer_lifespan.customer_id
              inner join cte_customer_recency
                on cte_revenue_per_period.customer_id = cte_customer_recency.customer_id
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final
  order by reporting_period desc,reporting_date desc, customer_id;

/* 
--------------------------------------------------------------------------------------------------------------------------------------------
PS: Records are not included if the revenue for the corresponding period is 0 as selected joins used are inner, meaning we see data only for customers that have implemented at least one order
---------------------------------------------------------------------------------------------------------------------------------------------
*/

"""

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

# # Writing to BigQuery

# In[5]:


# Defining the full table ID
full_table_id = f"{project_id}.{dataset_id}.{table_id}"

# Executing the query and storing the result in a dataframe
df = client.query(query).to_dataframe()

df['total_revenue'] = df['total_revenue'].astype('float64')
df['average_rentals_value'] = df['average_rentals_value'].astype('float64')
df['average_monthly_revenue'] = df['average_monthly_revenue'].astype('float64')

# Exploring some records
display(df.head())

# Defining table schema based on the project description

schema = [
    bigquery.SchemaField('customer_id', 'INTEGER'),
    bigquery.SchemaField('customer_name', 'STRING'),
    bigquery.SchemaField('first_rent', 'DATE'),
    bigquery.SchemaField('last_rent', 'DATE'),
    bigquery.SchemaField('customer_segment', 'STRING'),
    bigquery.SchemaField('recency', 'INTEGER'),
    bigquery.SchemaField('reporting_period', 'STRING'),
    bigquery.SchemaField('reporting_date', 'DATE'),
    bigquery.SchemaField('total_unique_orders', 'INTEGER'),
    bigquery.SchemaField('total_films_rented', 'INTEGER'),
    bigquery.SchemaField('total_revenue', 'FLOAT64'),
    bigquery.SchemaField('average_rentals_value', 'FLOAT64'),
    bigquery.SchemaField('average_monthly_revenue', 'FLOAT64'),
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
    subprocess.run(['python', '-m', 'jupyter', 'nbconvert', 'rep_customers_ordered.ipynb', '--to', 'python', '--output-dir=..'], check=True)
    print("Notebook successfully converted.")
except Exception as e:
    print(f"Notebook conversion skipped or failed: {e}")


# In[ ]:




