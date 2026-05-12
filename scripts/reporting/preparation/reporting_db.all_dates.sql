/*
===============================================================================
Date Dimension Generator (`reporting_db.all_dates`)
Dialect: BigQuery PostGres SQL

This script dynamically generates a comprehensive Date Dimension table. 
It creates a continuous, unbroken sequence of dates from 2015-01-01 to 
2026-12-05 and stages it in the reporting database.
===============================================================================
*/

create table if not exists `project-401f4646-3663-4125-aaa`.reporting_db.all_dates(
  date_column date
);

insert into `project-401f4646-3663-4125-aaa`.reporting_db.all_dates(date_column)
select 
date_add('2015-01-01',interval n day) as date_column
from
unnest(generate_array(0,date_diff('2026-12-05','2015-01-01',day))) as n;

--Checking data are inserted correctly in the table
--select * from `project-401f4646-3663-4125-aaa`.reporting_db.all_dates
--limit 50;
