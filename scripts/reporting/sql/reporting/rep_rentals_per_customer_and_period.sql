
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
          CAST(date_trunc(rent.rental_rental_date, day) AS DATE) as reporting_date, 
          cust.customer_id,
          count(*) as total_rentals
      from cte_rentals as rent left join cte_customers as cust 
            on rent.rental_customer_id = cust.customer_id
      group by reporting_period,reporting_date,cust.customer_id

      union all

      select
          'Month' as reporting_period,
          CAST(date_trunc(rent.rental_rental_date, month) AS DATE) as reporting_date, 
          cust.customer_id,
          count(*) as total_rentals
      from cte_rentals as rent left join cte_customers as cust 
            on rent.rental_customer_id = cust.customer_id
      group by reporting_period,reporting_date,cust.customer_id

      union all

      select
          'Year' as reporting_period,
          CAST(date_trunc(rent.rental_rental_date, year) AS DATE) as reporting_date,
          cust.customer_id,
          count(*) as total_rentals
      from cte_rentals as rent left join cte_customers as cust 
            on rent.rental_customer_id = cust.customer_id
      group by reporting_period,reporting_date,cust.customer_id

  )

 ,  cte_final as (

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_rentals_per_period.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates inner join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date
      where cte_reporting_dates.reporting_period = 'Day'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_rentals_per_period.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates inner join cte_rentals_per_period
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select 
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_rentals_per_period.customer_id,
          cte_rentals_per_period.total_rentals as total_rentals
      from cte_reporting_dates inner join cte_rentals_per_period 
        on cte_reporting_dates.reporting_period=cte_rentals_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_rentals_per_period.reporting_date 
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final;
