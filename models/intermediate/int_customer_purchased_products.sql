select
    i.customer_id,
    count(distinct p.product_code) as purchased_product_count,
    listagg(distinct p.product_code, ', ') within group (order by p.product_code) as purchased_products,
    count_if(p.product_code = 'ANALYTICS-ADDON') > 0 as has_expansion_product
from {{ ref('stg_netsuite_invoices') }} i
join {{ ref('stg_netsuite_invoice_lines') }} l on l.invoice_id = i.invoice_id
join {{ ref('stg_netsuite_items') }} p on p.item_id = l.item_id
group by i.customer_id
