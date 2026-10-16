select
    id as event_id,
    subscriberkey as subscriber_key,
    lower(event_type) as event_type,
    eventdate as event_at
from {{ ref('sfmc_event') }}
where eventdate < dateadd(day, 1, to_date('{{ var("demo_as_of_date") }}'))
