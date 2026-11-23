"""Central configuration (mirrors experiments/protocol.md)."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))          # Target_Journal_Submission
REPO = os.path.abspath(os.path.join(ROOT, ".."))
DATA_CACHE = os.environ.get("HYPO_DATA", os.path.join(REPO, "data_cache"))
RESULTS = os.path.join(ROOT, "results"); FIGURES = os.path.join(ROOT, "figures"); TABLES = os.path.join(ROOT, "tables")
SPLIT_SEED = 2026
MAP_THRESHOLD = 65.0
EVENT_MIN_DURATION = 5          # minutes
HORIZONS = [5, 10, 15, 30]
PRIMARY_H = 15
MIN_LEAD = 5                    # minutes
HISTORY_MIN = 30                # minutes of history required
HISTORY_VALID_FRAC = 0.7
REFRACTORY_AFTER_EVENT = 30     # minutes
ALARM_SILENCE = 10              # minutes
ALARM_BURDENS = [0.5, 1.0, 2.0] # alarms per patient-hour
NONOBVIOUS_MAP = 75.0
SEEDS = list(range(10))
N_BOOT = 1000
HP_BUDGET = 20
