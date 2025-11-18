{{ config(
    materialized = 'view',
    schema = 'BRONZE'
) }}

select
    tract_fips,
    rpl_theme1,
    rpl_theme2,
    rpl_theme3,
    rpl_theme4,
    rpl_themes
from {{ source('bronze', 'svi_ny_raw') }}
