-- Invoice amounts are aggregated before any line, opportunity, or event join.
select
    customer_id,
    count(*) as invoice_count,
    sum(invoice_amount) as invoice_amount,
    sum(paid_amount) as paid_invoice_amount,
    sum(unpaid_amount) as unpaid_invoice_amount,
    sum(case when due_date < to_date('{{ var("demo_as_of_date") }}')
             then unpaid_amount else 0 end) as overdue_invoice_amount
from {{ ref('stg_netsuite_invoices') }}
group by customer_id
