select customer_key
from {{ ref('customer_360') }}
where (customer_key = 'CUST-015' and (not has_expansion_product or expansion_eligible))
   or (customer_key = 'CUST-002' and overdue_invoice_amount <> 2000)
   or (customer_key = 'CUST-009' and unpaid_invoice_amount <> 2000)
   or paid_invoice_amount < 0 or overdue_invoice_amount < 0
union all
select customer_key
from {{ ref('expansion_audience') }}
where overdue_invoice_amount <> 0 or paid_invoice_amount <= 0
   or email_address not like '%@example.com'
