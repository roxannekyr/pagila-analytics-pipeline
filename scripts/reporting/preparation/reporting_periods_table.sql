/*
Reporting Periods Generator (`reporting_db.reporting_periods_table`)
Dialect: BigQuery Standard SQL   

This script establishes the structural schema for the Time-Intelligence 
dimension table. It defines the exact data types and columns required to store 
distinct business reporting intervals (Day, Week, Month, Quarter, Year).
*/

create table if not exists `project-401f4646-3663-4125-aaa`.reporting_db.reporting_periods_table(
  reporting_period string,
  reporting_date date
);

insert into `project-401f4646-3663-4125-aaa`.reporting_db.reporting_periods_table (reporting_period, reporting_date)

  with processed_dates as (
  select
    'Day' as reporting_period,
    date_trunc(date_column, day) as reporting_date,
  from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
  group by reporting_period,reporting_date
  union all
  select
    'Week' as reporting_period,
    date_trunc(date_column, week) as reporting_date,
  from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
  group by reporting_period,reporting_date
  union all
  select
    'Month' as reporting_period,
    date_trunc(date_column, month) as reporting_date,
  from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
  group by reporting_period,reporting_date
  union all
  select
    'Quarter' as reporting_period,
    date_trunc(date_column, quarter) as reporting_date,
  from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
  group by reporting_period,reporting_date
  union all
  select
    'Year' as reporting_period,
    date_trunc(date_column, year) as reporting_date,
  from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
  group by reporting_period,reporting_date
)
select *
from processed_dates
where reporting_date <= current_date;
