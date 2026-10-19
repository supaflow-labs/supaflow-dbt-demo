select
    account_id,
    count(*) as opportunity_count,
    count_if(is_won and is_closed) as won_opportunity_count,
    count_if(is_closed and not is_won) as lost_opportunity_count,
    sum(case when is_won and is_closed then amount else 0 end) as won_opportunity_amount
from {{ ref('stg_salesforce_opportunities') }}
group by account_id
