select
    customer_key, customer_name, email_address, subscriber_key,
    salesforce_account_id, netsuite_customer_id,
    paid_invoice_amount, overdue_invoice_amount, purchased_products,
    last_click_at, 'ANALYTICS-ADDON' as recommended_product,
    'Engaged customer with paid invoices, no overdue balance, and no analytics add-on' as audience_reason,
    as_of_date
from {{ ref('customer_360') }}
where expansion_eligible
