select
    id as account_id,
    name as customer_name,
    industry,
    isdeleted as is_deleted
from {{ ref('salesforce_account') }}
