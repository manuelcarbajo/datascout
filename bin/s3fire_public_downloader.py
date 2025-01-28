#!/usr/bin/env python3

import logging
import os

import boto3
from botocore import UNSIGNED
from botocore.config import Config


FIRE_ENDPOINT: str = "https://hl.fire.sdo.ebi.ac.uk"
PUBLIC_BUCKET: str = "era-public"

logging.basicConfig(level=logging.INFO)

def transform_ftp_to_s3(ftp_path):
    """
    Transforms an FTP path to a FIRE S3 object key, it also returns if it's public or private.
    """
    if ftp_path.startswith("ftp.sra.ebi.ac.uk/vol1/"):
        s3_key = ftp_path.replace("ftp.sra.ebi.ac.uk/vol1/", "")
        return s3_key
    else:
        raise ValueError(
            f"Invalid FTP path: {ftp_path}. Must start with 'ftp.sra.ebi.ac.uk/vol1/'"
        )


def download_file_from_fire(s3_key, outdir):
    """
    Downloads an individual file from FIRE S3 using its object key.
    """
    s3_args = {"endpoint_url": FIRE_ENDPOINT}
    # Public bucket configuration with unsigned requests
    s3_args.update({"config": Config(signature_version=UNSIGNED)})

    s3 = boto3.client("s3", **s3_args)
    local_file_path = os.path.join(outdir, os.path.basename(s3_key))

    try:
        logging.info(f"Downloading {s3_key} from S3 bucket {PUBLIC_BUCKET} to {local_file_path}...")
        s3.download_file(PUBLIC_BUCKET, s3_key, local_file_path)
        logging.info(f"File successfully downloaded to: {local_file_path}")
        return True
    except Exception as e:
        logging.info(f"Error downloading file from S3: {e}")
        return False
