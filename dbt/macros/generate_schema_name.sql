{% macro generate_schema_name(custom_schema_name, node) -%}
    {# default schema from the target (profile) #}
    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none or custom_schema_name == '' -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | upper }}
    {%- endif -%}
{%- endmacro %}
