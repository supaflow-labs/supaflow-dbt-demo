select
    id as opportunity_id,
    accountid as account_id,
    amount,
    closedate as close_date,
    iswon as is_won,
    isclosed as is_closed,
    isdeleted as is_deleted
from {{ ref('salesforce_opportunity') }}
where not coalesce(isdeleted, false)
  and (not coalesce(isclosed, false) or closedate <= to_date('{{ var("demo_as_of_date") }}'))
