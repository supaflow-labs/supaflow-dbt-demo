select
    uniquekey as invoice_line_id,
    transaction as invoice_id,
    item as item_id,
    -netamount as line_amount
from {{ ref('netsuite_transactionline') }}
where mainline = 'F' and taxline = 'F'
