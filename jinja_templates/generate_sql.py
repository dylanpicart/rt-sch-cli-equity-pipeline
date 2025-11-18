import argparse
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR
CONFIG_FILE = BASE_DIR / "config.yml"


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def render_template(env: Environment, template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


def main():
    parser = argparse.ArgumentParser(
        description="Render Jinja2 templates for SQL/dbt profiles."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=str(CONFIG_FILE),
        help="YAML config file path.",
    )
    args = parser.parse_args()

    cfg = load_config(Path(args.config))

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Example: render dbt profiles.yml
    profiles_ctx = cfg.get("dbt_profile", {})
    profiles_sql = render_template(env, "dbt_env_template.yml.j2", profiles_ctx)
    (BASE_DIR.parent / "dbt" / "profiles.generated.yml").write_text(profiles_sql)
    print("Generated dbt profiles → dbt/profiles.generated.yml")

    # Example: render a metric query
    if "metric_query" in cfg:
        mq_ctx = cfg["metric_query"]
        metric_sql = render_template(env, "metric_query.sql.j2", mq_ctx)
        (BASE_DIR / "metric_query.generated.sql").write_text(metric_sql)
        print("Generated metric query → jinja_templates/metric_query.generated.sql")


if __name__ == "__main__":
    main()
