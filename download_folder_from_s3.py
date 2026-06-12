#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tqdm import tqdm

load_dotenv()

ENDPOINT_URL = os.environ["S3_ENDPOINT_URL"]


def make_progress_callback(name: str, size: int):
    pbar = tqdm(total=size, unit="B", unit_scale=True, desc=name)
    seen = 0

    def callback(bytes_amount: int):
        nonlocal seen
        seen += bytes_amount
        pbar.update(bytes_amount)
        if seen >= size:
            pbar.close()

    return callback


def iter_objects(s3, bucket: str, prefix: str):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield obj["Key"], obj["Size"]


def download_folder(bucket: str, prefix: str, destination: str) -> bool:
    s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)
    dest_root = Path(destination)

    try:
        keys = list(iter_objects(s3, bucket, prefix))
    except NoCredentialsError:
        print("no credentials found, check .env", file=sys.stderr)
        return False
    except ClientError as e:
        print(f"listing failed: {e}", file=sys.stderr)
        return False

    if not keys:
        print(f"nothing found under s3://{bucket}/{prefix}", file=sys.stderr)
        return False

    print(f"found {len(keys)} object(s) under s3://{bucket}/{prefix}")
    failed = 0
    for key, size in keys:
        if key.endswith("/"):
            continue
        local_path = dest_root / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            progress = make_progress_callback(key.split("/")[-1], size)
            s3.download_file(bucket, key, str(local_path), Callback=progress)
        except ClientError as e:
            print(f"download failed for {key}: {e}", file=sys.stderr)
            failed += 1
        except Exception as e:
            print(f"unexpected error for {key}: {e}", file=sys.stderr)
            failed += 1

    if failed:
        print(f"completed with {failed} failure(s)", file=sys.stderr)
        return False

    print(f"download complete: s3://{bucket}/{prefix} -> {dest_root}")
    return True


def main():
    bucket = input("bucket: ").strip()
    prefix = input("prefix (folder, empty for whole bucket): ").strip()
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    destination = input("destination [.]: ").strip() or "."

    sys.exit(0 if download_folder(bucket, prefix, destination) else 1)


if __name__ == "__main__":
    main()
