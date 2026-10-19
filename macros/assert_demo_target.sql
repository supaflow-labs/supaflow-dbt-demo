{% macro assert_demo_target() %}
  {% set schema = target.schema | upper %}
  {% if target.database | upper != 'SUPA_DB' or not modules.re.match('^SUPAFLOW_DEMO(?:_[A-Z0-9]+)*$', schema) %}
    {{ exceptions.raise_compiler_error('Use SUPA_DB with dedicated schema SUPAFLOW_DEMO or SUPAFLOW_DEMO_<SUFFIX>.') }}
  {% endif %}
  {{ return('select 1') }}
{% endmacro %}
