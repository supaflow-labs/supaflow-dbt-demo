with assessed as (
    select
        x.customer_key,
        a.customer_name,
        a.industry,
        x.account_id as salesforce_account_id,
        x.netsuite_customer_id,
        x.subscriber_key,
        s.email_address,
        s.subscription_status,
        coalesce(o.won_opportunity_count, 0) as won_opportunity_count,
        coalesce(o.won_opportunity_amount, 0) as won_opportunity_amount,
        coalesce(f.paid_invoice_amount, 0) as paid_invoice_amount,
        coalesce(f.unpaid_invoice_amount, 0) as unpaid_invoice_amount,
        coalesce(f.overdue_invoice_amount, 0) as overdue_invoice_amount,
        p.purchased_products,
        coalesce(p.has_expansion_product, false) as has_expansion_product,
        e.last_click_at,
        to_date('{{ var("demo_as_of_date") }}') as as_of_date,
        case
            when a.account_id is null then 'missing_salesforce_match'
            when coalesce(a.is_deleted, false) then 'deleted_account'
            when coalesce(o.won_opportunity_count, 0) = 0 then
                case when o.lost_opportunity_count > 0 then 'closed_lost' else 'no_closed_won' end
            when n.customer_id is null then 'missing_finance_match'
            when n.is_inactive then 'inactive_finance_customer'
            when coalesce(f.overdue_invoice_amount, 0) > 0 then 'overdue_invoice'
            when s.subscription_status = 'Unsubscribed' or s.unsubscribed_at is not null then 'unsubscribed'
            when s.subscription_status = 'Held' then 'held_subscriber'
            when s.subscription_status is null or s.subscription_status <> 'Active' then 'unknown_subscription_status'
            when e.has_complaint then 'complaint_event'
            when e.has_unsubscribe then 'unsubscribe_event'
            when coalesce(f.paid_invoice_amount, 0) <= 0 then 'no_paid_invoice'
            when coalesce(p.has_expansion_product, false) then 'already_has_expansion_product'
            when e.last_click_at is null then 'no_engagement'
            when e.last_click_at < dateadd(day, -30, to_date('{{ var("demo_as_of_date") }}')) then 'stale_engagement'
            else 'eligible'
        end as eligibility_reason
    from {{ ref('stg_customer_identity') }} x
    left join {{ ref('stg_salesforce_accounts') }} a on a.account_id = x.account_id
    left join {{ ref('int_sales_pipeline_summary') }} o on o.account_id = x.account_id
    left join {{ ref('stg_netsuite_customers') }} n on n.customer_id = x.netsuite_customer_id
    left join {{ ref('int_customer_financial_health') }} f on f.customer_id = n.customer_id
    left join {{ ref('int_customer_purchased_products') }} p on p.customer_id = n.customer_id
    left join {{ ref('stg_sfmc_subscribers') }} s on s.subscriber_key = x.subscriber_key
    left join {{ ref('int_customer_engagement') }} e on e.subscriber_key = x.subscriber_key
)
select *, eligibility_reason = 'eligible' as expansion_eligible
from assessed
