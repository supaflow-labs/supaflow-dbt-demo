select
    id as invoice_id,
    entity as customer_id,
    trandate as invoice_date,
    duedate as due_date,
    foreigntotal as invoice_amount,
    foreignamountpaid as paid_amount,
    foreignamountunpaid as unpaid_amount
from {{ ref('netsuite_transaction') }}
where type = 'CustInvc' and voided = 'F' and currency = 1
  and trandate <= to_date('{{ var("demo_as_of_date") }}')
