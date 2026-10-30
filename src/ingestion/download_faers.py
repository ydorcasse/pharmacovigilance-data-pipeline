# Import libraries
import os 
from pathlib import Path
import argparse

from dotenv import load_dotenv
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
    
# Define paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

# Load configuration
def load_aws_config():
    load_dotenv()

    config = {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_default_region": os.getenv("AWS_DEFAULT_REGION"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
    }

    for name, value in config.items():
        if not value:
            raise ValueError(f"Configuration manquante : {name}")

    return config

# Build faers url 
def build_faers_url(year: int, quarter: int) -> str:
    """Construit l'url de téléchargement du fichier FAERS ASCII pour un trimestre donné."""
    
    if year < 2004:
        raise ValueError("L'année doit être supérieure ou égale à 2004")
    if not 1 <= quarter <= 4:
        raise ValueError("Le trimestre doit être compris entre 1 et 4")
    url = f"https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip"
    return url

# Download the FAERS file
def download_faers_file(url: str) -> Path:
    """Télécharge le fichier FAERS depuis l'URL et l'enregistre dans data/bronze."""
    
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url, timeout=(10, 60))
    response.raise_for_status() # échoue si erreur HTTP
    file_name = Path(url).name
    file_path = BRONZE_DIR / file_name
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

# Upload to S3
def upload_to_s3(s3_client, bucket: str, file_path: Path) -> None:
    """Envoie le fichier local vers le bucket S3."""
    
    key = file_path.name
    s3_client.upload_file(str(file_path), bucket, key)

# Verify if an object exists into a bucket    
def s3_object_exists(s3_client, bucket: str, key: str) -> bool:
    """Retourne True si l'objet existe déjà dans le bucket."""
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise
    
if __name__ == "__main__":
    
    # Arguments CLI
    parser = argparse.ArgumentParser(description="Ingest a FAERS quarter to S3")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--quarter", type=int, required=True)
    args = parser.parse_args()
    
    # Construction de l'URL
    try:
        url = build_faers_url(args.year, args.quarter)
        print(f"URL construite : {url}")
    except ValueError as exc:
        parser.error(str(exc))
    
    key = Path(url).name
    file_path = BRONZE_DIR / key
    
    
    # Chargement de la configuration AWS
    try:
        config = load_aws_config()
    except ValueError as exc:
        parser.error(str(exc))
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=config["aws_access_key_id"],
        aws_secret_access_key=config["aws_secret_access_key"],
        region_name=config["aws_default_region"]
    )
    
    #  Téléchargement
    if file_path.exists():
        print(f"{key} déjà présent en local.")
    else:
        try:
            file_path = download_faers_file(url)
            print(f"Téléchargement réussi : {file_path}")
        except requests.exceptions.RequestException as exc:
            print(f"Echec du téléchargement de {url} : {exc}")
            raise SystemExit(1)
    
    # Upload
    if s3_object_exists(s3_client, config["s3_bucket_name"], key):
        print(f"{key} déjà présent dans S3.")
    else:
        try:
            upload_to_s3(s3_client, config["s3_bucket_name"], file_path)
            print("Envoi vers S3 réussi.")
        except (BotoCoreError, ClientError) as exc:
            print(f"Echec de l'envoi vers S3 : {exc}")
            raise SystemExit(1)