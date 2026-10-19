select
    id as customer_id,
    companyname as company_name,
    isinactive = 'T' as is_inactive
from {{ ref('netsuite_customer') }}
