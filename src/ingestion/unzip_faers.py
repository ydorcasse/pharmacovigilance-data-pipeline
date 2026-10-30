# Import libraries
import zipfile
from pathlib import Path
import argparse

# Define Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

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
        print(f"{zip_path.stem} déjà décompressé.")
    
    unzip_path.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(unzip_path)
        
    return unzip_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unzip a FAERS quarter")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--quarter", type=int, required=True)
    args = parser.parse_args()
    
    try:
        extract_dir = unzip_faers(args.year, args.quarter)
        print(f"Extraction terminé dans : {extract_dir}")
    except ValueError as exc:
        parser.error(str(exc))
    except FileNotFoundError as exc:
        parser.error(str(exc))
    except zipfile.BadZipFile as exc:
        parser.error(f"Le fichier ZIP est invalide : {exc}")