# Import libraries
import os 
from pathlib import Path

from dotenv import load_dotenv
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Load configuration
load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_default_region = os.getenv("AWS_DEFAULT_REGION")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")

required_vars = {
    "AWS_ACCESS_KEY_ID": aws_access_key_id,
    "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
    "AWS_DEFAULT_REGION": aws_default_region,
    "S3_BUCKET_NAME": s3_bucket_name
}

# Validation
for name, value in required_vars.items():
    if value is None:
        raise ValueError(f"Variable d'environnement manquante : {name}")
    
# Define paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

# Build faers url 
def build_faers_url(year: int, quarter: int) -> str:
    """Construit l'url de téléchargement du fichier FAERS ASCII pour un trimestre donné."""
    
    url = f"https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip"
    return url

# Download the FAERS file
def download_faers_file(url: str) -> Path:
    """Télécharge le fichier FAERS depuis l'URL et l'enregistre dans data/bronze."""
    
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=(10, 120))
    response.raise_for_status() # échoue si erreur HTTP
    file_name = Path(url).name
    file_path = BRONZE_DIR / file_name
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

# Upload to S3
def upload_to_s3(file_path: Path) -> None:
    """Envoie le fichier local vers le bucket S3."""
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_default_region
    )
    key = file_path.name
    s3_client.upload_file(str(file_path), s3_bucket_name, key)
    
if __name__ == "__main__":
    year, quarter = 2026, 2
    url = build_faers_url(year, quarter)
    print(f"URL construite : {url}")

    try:
        file_path = download_faers_file(url)
        print(f"Téléchargement réussi : {file_path}")
    except requests.exceptions.RequestException as exc:
        print(f"Échec du téléchargement de {url} : {exc}")
        raise SystemExit(1)

    try:
        upload_to_s3(file_path)
        print("Envoi vers S3 réussi")
    except (BotoCoreError, ClientError) as exc:
        print(f"Échec de l'envoi vers S3 : {exc}")
        raise SystemExit(1)