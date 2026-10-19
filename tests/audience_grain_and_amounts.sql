with actual as (
    select * from {{ ref('customer_360') }}
)
select customer_key
from actual
group by customer_key
having count(*) <> 1
union all
select customer_key
from actual
where (customer_key = 'CUST-001' and (paid_invoice_amount <> 12200 or overdue_invoice_amount <> 0))
   or (customer_key = 'CUST-009' and (paid_invoice_amount <> 11800 or overdue_invoice_amount <> 0))
