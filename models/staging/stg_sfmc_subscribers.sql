select
    subscriberkey as subscriber_key,
    emailaddress as email_address,
    status as subscription_status,
    unsubscribeddate as unsubscribed_at
from {{ ref('sfmc_subscribers') }}
