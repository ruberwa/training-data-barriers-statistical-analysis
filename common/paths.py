from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "Ready Analysis dataset.xlsx"
CONFIG_DIR = BASE_DIR / "config"
ANALYSIS_CONFIG = CONFIG_DIR / "analysis-config.yaml"
BOOTSTRAP_CONFIG = CONFIG_DIR / "bootstrap-config.yaml"
RESEARCH_QUESTION_MAP = CONFIG_DIR / "research-question-map.yaml"
FIGURES_CONFIG = CONFIG_DIR / "figures"
RESULTS_DIR = BASE_DIR / "results"
ANALYSIS_READY_DIR = RESULTS_DIR / "analysis_ready_tables"
ANALYSIS_READY_CSV_DIR = ANALYSIS_READY_DIR / "csv"
STATISTICS_DIR = RESULTS_DIR / "statistics"
STATISTICS_CSV_DIR = STATISTICS_DIR / "csv"
FIGURES_DIR = RESULTS_DIR / "figures"
MAP_FILE = BASE_DIR / "data" / "maps" / "naturalearth_lowres.shp"
VALIDATION_DIR = RESULTS_DIR / "validation"
LOGS_DIR = RESULTS_DIR / "logs"
