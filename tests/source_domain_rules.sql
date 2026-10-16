select 'customer_checkbox' as violation
from {{ ref('netsuite_customer') }} where isinactive not in ('T', 'F')
union all
select 'invoice_currency_or_flag'
from {{ ref('netsuite_transaction') }} where currency <> 1 or voided not in ('T', 'F')
union all
select 'future_event'
from {{ ref('sfmc_event') }}
where eventdate >= dateadd(day, 1, to_date('{{ var("demo_as_of_date") }}'))
union all
select 'non_synthetic_email'
from {{ ref('sfmc_subscribers') }} where emailaddress not like '%@example.com'
union all
select 'non_synthetic_finance_email'
from {{ ref('netsuite_customer') }} where email not like '%@example.com'
