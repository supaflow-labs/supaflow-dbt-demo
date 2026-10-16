select
    customer_key,
    salesforce_account_id as account_id,
    netsuite_customer_id,
    sfmc_subscriber_key as subscriber_key
from {{ ref('customer_identity') }}
