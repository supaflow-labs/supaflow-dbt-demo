select
    customer_key, customer_name, eligibility_reason,
    subscription_status, paid_invoice_amount, overdue_invoice_amount,
    has_expansion_product, last_click_at, as_of_date
from {{ ref('customer_360') }}
where not expansion_eligible
