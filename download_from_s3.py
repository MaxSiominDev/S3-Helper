#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tqdm import tqdm

load_dotenv()


def make_progress_callback(key: str, size: int):
    pbar = tqdm(total=size, unit="B", unit_scale=True, desc=key.split("/")[-1])
    seen = 0

    def callback(bytes_amount: int):
        nonlocal seen
        seen += bytes_amount
        pbar.update(bytes_amount)
        if seen >= size:
            pbar.close()

    return callback


def download_file(bucket: str, object_key: str, destination: str) -> bool:
    s3 = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL"))

    dest = Path(destination)
    local_path = dest / object_key.split("/")[-1] if dest.is_dir() else dest

    try:
        size = s3.head_object(Bucket=bucket, Key=object_key)["ContentLength"]
        progress = make_progress_callback(object_key, size)
        print(f"downloading s3://{bucket}/{object_key} -> {local_path}")
        s3.download_file(bucket, object_key, str(local_path), Callback=progress)
        print(f"download complete: {bucket}/{object_key}")
        return True
    except NoCredentialsError:
        print("no credentials found, check .env", file=sys.stderr)
    except ClientError as e:
        print(f"download failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"unexpected error: {e}", file=sys.stderr)
    return False


def main():
    bucket = input("bucket: ").strip()
    object_key = input("object key: ").strip()
    destination = input("destination [.]: ").strip() or "."

    sys.exit(0 if download_file(bucket, object_key, destination) else 1)


if __name__ == "__main__":
    main()