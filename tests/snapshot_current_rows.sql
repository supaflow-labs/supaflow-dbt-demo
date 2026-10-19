with actual as (
    select subscriber_key, count(*) as versions
    from {{ ref('subscriber_status_history') }}
    where dbt_valid_to is null
    group by subscriber_key
)
select coalesce(a.subscriber_key, s.subscriber_key) as subscriber_key
from actual a full outer join {{ ref('stg_sfmc_subscribers') }} s using (subscriber_key)
where a.subscriber_key is null or s.subscriber_key is null or a.versions <> 1
