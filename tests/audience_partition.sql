with expected as (
    select customer_key, expansion_eligible from {{ ref('customer_360') }}
), actual as (
    select customer_key, true as expansion_eligible from {{ ref('expansion_audience') }}
    union all
    select customer_key, false as expansion_eligible from {{ ref('excluded_customers') }}
)
select coalesce(e.customer_key, a.customer_key) as customer_key
from expected e full outer join actual a using (customer_key)
where e.customer_key is null or a.customer_key is null
   or e.expansion_eligible is distinct from a.expansion_eligible
