with line_totals as (
    select transaction, -sum(netamount) as invoiced_amount
    from {{ ref('netsuite_transactionline') }}
    where mainline = 'F' and taxline = 'F'
    group by transaction
)
select t.id
from {{ ref('netsuite_transaction') }} t
left join line_totals l on l.transaction = t.id
where t.voided = 'F'
  and (t.foreigntotal is distinct from t.foreignamountpaid + t.foreignamountunpaid
       or t.foreigntotal is distinct from l.invoiced_amount
       or t.foreignamountunpaid < 0 or t.foreignamountpaid < 0)
