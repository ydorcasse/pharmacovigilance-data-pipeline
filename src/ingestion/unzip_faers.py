# Import libraries
import zipfile
import logging
from src.utils.logging_config import setup_logging
from pathlib import Path
import argparse

# Define Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

# Logging
logger = logging.getLogger(__name__)

def unzip_faers(year: int, quarter: int) -> Path:
    if year < 2004:
        raise ValueError("L'année doit être supérieure ou égale à 2004")
    if not 1 <= quarter <= 4:
        raise ValueError("Le trimestre doit être compris entre 1 et 4")
    
    # Chemin du zip
    zip_path = BRONZE_DIR / f"faers_ascii_{year}q{quarter}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Fichier ZIP introuvable : {zip_path}")
    
    # chemin d'extraction
    unzip_path = BRONZE_DIR / zip_path.stem
    
    if unzip_path.exists():
        logger.info(f"{zip_path.stem} déjà décompressé, extraction ignorée.")
        return unzip_path
    
    unzip_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Décompression de {zip_path.name}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(unzip_path)
    logger.info(f"Décompression terminée : {unzip_path}")   
    
    return unzip_path

if __name__ == "__main__":
    
    # Setup logging
    setup_logging()
    
    # Arguments CLI
    parser = argparse.ArgumentParser(description="Unzip a FAERS quarter")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--quarter", type=int, required=True)
    args = parser.parse_args()
    
    try:
        extract_dir = unzip_faers(args.year, args.quarter)
        logger.info(f"Extraction terminé dans : {extract_dir}")
    except ValueError:
        logger.exception(f"Année {args.year} ou trimestre {args.quarter} pas correct.")
        raise SystemExit(1)
    except FileNotFoundError:
        logger.exception("Fichier ZIP introuvable")
        raise SystemExit(1)
    except zipfile.BadZipFile:
        logger.exception("Fichier zip corrompu")
        raise SystemExit(1)