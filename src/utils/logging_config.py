import logging
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs"

def setup_logging(level=logging.INFO):
    """Console + fichier applicatif (INFO) + fichier erreur (ERROR), datés du jour."""
    
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    
    # Console (INFO+), visible à l'exécution
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    
    # Fichier applicatif : toutes les utilisations (INFO et au-dessus)
    app_handler = logging.FileHandler(LOGS_DIR / f"app_{today}.log", encoding="utf-8")
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    
    # Fichier erreurs : ERREURS uniquement 
    error_handler = logging.FileHandler(LOGS_DIR / f"errors_{today}.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Evite d'ajouter les handlers deux fois si la fonction est appelée plusieurs fois
    if not root_logger.handlers:
        root_logger.addHandler(console)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)