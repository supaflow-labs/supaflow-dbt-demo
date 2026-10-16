{% snapshot subscriber_status_history %}
{{ config(
    unique_key='subscriber_key',
    strategy='check',
    check_cols=['subscription_status', 'email_address', 'unsubscribed_at'],
    schema='SNAPSHOTS'
) }}
select * from {{ ref('stg_sfmc_subscribers') }}
{% endsnapshot %}
