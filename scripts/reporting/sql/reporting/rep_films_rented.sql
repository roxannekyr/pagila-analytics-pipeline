
  with cte_film as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_film`

  )
  , cte_film_category as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_film_category`
  )

  , cte_category as (
    select *
    from `project-401f4646-3663-4125-aaa.staging_db.stg_category`
  )

    , cte_rentals as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_rental`

  )

  , cte_reporting_dates as (

      select * 
      from `project-401f4646-3663-4125-aaa.reporting_db.reporting_periods_table`
      where reporting_period in ('Day','Month','Year') and reporting_date >= cast('2015-01-01' as date)

  )

  , cte_inventory as (

      select *
      from `project-401f4646-3663-4125-aaa.staging_db.stg_inventory`
  )

  , cte_film_lifespan as (
    select
        inv.inventory_film_id as film_id,
        cast(min(rent.rental_rental_date) as date) as first_rent,
        cast(max(rent.rental_rental_date) as date) as last_rent,
        date_diff(cast(max(rent.rental_rental_date) as date),cast(min(rent.rental_rental_date) as date),month) as     film_lifespan
    from cte_rentals as rent
    inner join cte_inventory as inv
        on rent.rental_inventory_id = inv.inventory_id
    group by inv.inventory_film_id

  )
  
  , cte_payment as (

      select * 
      from `project-401f4646-3663-4125-aaa.staging_db.stg_payment`

  )
    
  ,  cte_revenue_per_period as (

      select
          category.category_id,
          category.category_name,
          film.film_id,
          film.film_title,
          'Day' as reporting_period,
          cast(date_trunc(rent.rental_rental_date, day) as date) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_film_category as film_category
                    on film.film_id = film_category.film_category_film_id
                      left join cte_category as category
                          on film_category.film_category_category_id = category.category_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by category.category_id,category.category_name,film.film_id,film.film_title,reporting_period,reporting_date

      union all

      select
          category.category_id,
          category.category_name,
          film.film_id,
          film.film_title,
          'Month' as reporting_period,
          cast(date_trunc(rent.rental_rental_date, month) as date) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_film_category as film_category
                    on film.film_id = film_category.film_category_film_id
                      left join cte_category as category
                          on film_category.film_category_category_id = category.category_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by category.category_id,category.category_name,film.film_id,film.film_title,reporting_period,reporting_date

      union all

      select
          category.category_id,
          category.category_name,
          film.film_id,
          film.film_title,
          'Year' as reporting_period,
          cast(date_trunc(rent.rental_rental_date, year) as date) as reporting_date,
          count(distinct rent.rental_id) total_unique_orders,
          sum(payment_amount) as total_revenue
      from cte_rentals as rent
      left join cte_payment as payment 
        on rent.rental_id=payment.payment_rental_id
          left join cte_inventory as inv
            on rent.rental_inventory_id=inv.inventory_id
              left join cte_film as film
                on inv.inventory_film_id=film.film_id
                  left join cte_film_category as film_category
                    on film.film_id = film_category.film_category_film_id
                      left join cte_category as category
                          on film_category.film_category_category_id = category.category_id
      where film_title not in ('GOODFELLAS SALUTE')
      group by category.category_id,category.category_name,film.film_id,film.film_title,reporting_period,reporting_date

  )

 ,  cte_final as (

      select
          cte_revenue_per_period.category_id,
          cte_revenue_per_period.category_name,
          cte_revenue_per_period.film_id,
          cte_revenue_per_period.film_title,
          cte_film_lifespan.first_rent,
          cte_film_lifespan.last_rent,
          case when cte_film_lifespan.film_lifespan >= 12 then 'High-Performer'
					     when cte_film_lifespan.film_lifespan >= 6 then 'Mid-Performer'
					     else 'New'
				  end as product_segment,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_unique_orders as total_unique_orders,
          cte_revenue_per_period.total_revenue as total_revenue,
          case when total_unique_orders  = 0 then 0
			        else round(cte_revenue_per_period.total_revenue * 1.0 / cte_revenue_per_period.total_unique_orders, 2)			
		      end as avg_order_revenue, 
		      case when cte_film_lifespan.film_lifespan = 0 then cte_revenue_per_period.total_revenue
			        else round(cte_revenue_per_period.total_revenue * 1.0 / cte_film_lifespan.film_lifespan, 2)					
		      end as avg_monthly_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on (cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date)
          inner join cte_film_lifespan 
            on cte_revenue_per_period.film_id = cte_film_lifespan.film_id
      where cte_reporting_dates.reporting_period = 'Month'

      union all

      select
          cte_revenue_per_period.category_id,
          cte_revenue_per_period.category_name,
          cte_revenue_per_period.film_id,
          cte_revenue_per_period.film_title,
          cte_film_lifespan.first_rent,
          cte_film_lifespan.last_rent,
          case when cte_film_lifespan.film_lifespan >= 12 then 'High-Performer'
					     when cte_film_lifespan.film_lifespan >= 6 then 'Mid-Performer'
					     else 'New'
				  end as product_segment,
          cte_reporting_dates.reporting_period,
          cte_reporting_dates.reporting_date,
          cte_revenue_per_period.total_unique_orders as total_unique_orders,
          cte_revenue_per_period.total_revenue as total_revenue,
          case when total_unique_orders  = 0 then 0
			        else round(cte_revenue_per_period.total_revenue * 1.0 / cte_revenue_per_period.total_unique_orders, 2)			
		      end as avg_order_revenue, 
		      case when cte_film_lifespan.film_lifespan = 0 then cte_revenue_per_period.total_revenue
			        else round(cte_revenue_per_period.total_revenue * 1.0 / cte_film_lifespan.film_lifespan, 2)					
		      end as avg_monthly_revenue
      from cte_reporting_dates inner join cte_revenue_per_period
        on (cte_reporting_dates.reporting_period=cte_revenue_per_period.reporting_period 
        and cte_reporting_dates.reporting_date=cte_revenue_per_period.reporting_date)
          inner join cte_film_lifespan 
            on cte_revenue_per_period.film_id = cte_film_lifespan.film_id
      where cte_reporting_dates.reporting_period = 'Year'

 )

  select * from cte_final
  order by reporting_period desc,reporting_date desc, film_id;

/* 
---------------------------------------------------------------------------------------------------------------------------
PS: Records are not included if the revenue for the corresponding period is 0 as selected joins used are inner, meaning we see data only for films that have at least been ordered once
---------------------------------------------------------------------------------------------------------------------------
*/

