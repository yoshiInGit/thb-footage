from app.pipeline import Pipeline
from app.utils import load_config
import os

from app.constants import PLAN_FILE, SETTINGS_YAML

def main():
    config = load_config(SETTINGS_YAML)
    pipeline = Pipeline(config)
    pipeline.run_with_control()

if __name__ == "__main__":
    main()
