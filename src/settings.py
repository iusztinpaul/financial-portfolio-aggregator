from pathlib import Path

STORAGE_PATH = str(Path.home() / '.financial-portfolio-aggregator')
Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)
