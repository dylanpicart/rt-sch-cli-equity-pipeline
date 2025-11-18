{{ config(
    materialized = 'table',
    schema = 'SILVER'
) }}

with base as (

    select
        tract_fips,
        rpl_theme1,
        rpl_theme2,
        rpl_theme3,
        rpl_theme4,
        rpl_themes
    from {{ ref('bronze_svi') }}

),

scored as (

    select
        tract_fips,
        rpl_theme1,
        rpl_theme2,
        rpl_theme3,
        rpl_theme4,
        rpl_themes,
        case
            when rpl_themes is null then 'Unknown'
            when rpl_themes < 0.33 then 'Low'
            when rpl_themes < 0.66 then 'Moderate'
            else 'High'
        end as svi_overall_bucket,
        case
            when rpl_theme1 is null then 'Unknown'
            when rpl_theme1 < 0.33 then 'Low'
            when rpl_theme1 < 0.66 then 'Moderate'
            else 'High'
        end as svi_socioeconomic_bucket
    from base

)

select * from scored
