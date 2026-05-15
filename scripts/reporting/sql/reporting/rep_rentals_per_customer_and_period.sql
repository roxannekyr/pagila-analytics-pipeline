    with cte_rentals as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`

  )

  , cte_reporting_dates as (

      select * 
      from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
      where reporting_period in ('Day','Month','Year')

  )

  ,  cte_customers as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_customer`

  )

  ,  cte_rentals_per_period as (

      select
          'Day' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), day) as reporting_date,   -- if timestamp aggregated in daily level
          cte_customers.customer_id,
          count(*) as total_rentals
      from cte_rentals as rentals
        left join cte_customers
          on cte_customers.customer_id=rentals.rental_customer_id

      group by reporting_period,reporting_date,cte_customers.customer_id

      union all

      select
          'Month' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), month) as reporting_date,   -- if timestamp aggregated in monthly level
          cte_customers.customer_id,
          count(*) as total_rentals
      from cte_rentals as rentals
        left join cte_customers
          on cte_customers.customer_id=rentals.rental_customer_id

      group by reporting_period,reporting_date,cte_customers.customer_id

      union all

      select
          'Year' as reporting_period,
          date_trunc(date(rentals.rental_rental_date), year) as reporting_date,   -- if timestamp aggregated in yearly level
          cte_customers.customer_id,
          count(*) as total_rentals
      from cte_rentals as rentals
        left join cte_customers
          on cte_customers.customer_id=rentals.rental_customer_id

      group by reporting_period,reporting_date,cte_customers.customer_id

  )

 ,  cte_final as (

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_customers.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date
          left join cte_customers 
            on cte_rentals_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_customers.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date
          left join cte_customers 
            on cte_rentals_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_customers.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates left join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date
          left join cte_customers 
            on cte_rentals_per_period.customer_id=cte_customers.customer_id
      where cte_reporting_dates.reporting_period = 'Year'

 )
    select * from cte_final
    order by total_rentals DESC;

    /* Checking the total numbers for daily level */
    
    /*
    select 
        sum(total_rentals) as total_rentals
    from cte_final
    where reporting_period = 'Day';  
    */
    
   
