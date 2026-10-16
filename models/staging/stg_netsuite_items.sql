select
    id as item_id,
    itemid as product_code,
    displayname as product_name,
    isinactive = 'T' as is_inactive
from {{ ref('netsuite_item') }}
