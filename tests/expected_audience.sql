with actual as (
    select * from {{ ref('customer_360') }}
), expected as (
    select * from {{ ref('demo_scenarios') }}
)
select coalesce(a.customer_key, e.customer_key) as customer_key
from actual a
full outer join expected e on e.customer_key = a.customer_key
where a.customer_key is null or e.customer_key is null
   or a.expansion_eligible is distinct from e.expected_eligible
   or a.eligibility_reason is distinct from e.expected_reason
