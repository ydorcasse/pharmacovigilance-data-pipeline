import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs"

def setup_logging(level=logging.INFO):
    """Configure le logging pour tout le projet."""
    
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    
    # Sortie console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    
    # Sortie fichier avec rotation quotidienne
    fichier = TimedRotatingFileHandler(
        LOGS_DIR / "faers.log", when="midnight", backupCount=7, encoding="utf-8"
    )
    fichier.setFormatter(formatter)
    
    # Configuartion du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Evite d'ajouter les handlers deux fois si la fonction est appelée plusieurs fois
    if not root_logger.handlers:
        root_logger.addHandler(console)
        root_logger.addHandler(fichier)