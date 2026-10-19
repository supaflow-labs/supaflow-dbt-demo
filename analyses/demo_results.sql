select
    customer_name,
    paid_invoice_amount,
    overdue_invoice_amount,
    recommended_product
from {{ ref('expansion_audience') }}
order by customer_key
