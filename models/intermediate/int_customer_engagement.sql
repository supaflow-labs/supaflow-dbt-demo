select
    subscriber_key,
    count(*) as event_count,
    max(case when event_type = 'click' then event_at end) as last_click_at,
    count_if(event_type = 'unsubscribe') > 0 as has_unsubscribe,
    count_if(event_type = 'complaint') > 0 as has_complaint
from {{ ref('stg_sfmc_events') }}
group by subscriber_key
