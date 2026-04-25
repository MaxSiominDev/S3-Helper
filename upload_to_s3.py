#!/usr/bin/env python3

import sys
import os
from pathlib import Path

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from tqdm import tqdm

load_dotenv()

ENDPOINT_URL = os.environ["S3_ENDPOINT_URL"]


class ProgressPercentage:
    def __init__(self, filepath: Path):
        self._size = filepath.stat().st_size
        self._seen_so_far = 0
        self._pbar = tqdm(total=self._size, unit="B", unit_scale=True, desc=filepath.name)

    def __call__(self, bytes_amount: int):
        self._seen_so_far += bytes_amount
        self._pbar.update(bytes_amount)
        if self._seen_so_far >= self._size:
            self._pbar.close()


def upload_file(local_path: str, bucket: str, object_key: str) -> bool:
    local_file = Path(local_path)
    if not local_file.is_file():
        print(f"'{local_path}' is not a file", file=sys.stderr)
        return False

    s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)

    try:
        print(f"uploading {local_file} -> s3://{bucket}/{object_key}")
        s3.upload_file(str(local_file), bucket, object_key, Callback=ProgressPercentage(local_file))
        print(f"upload complete: s3://{bucket}/{object_key}")
        return True
    except NoCredentialsError:
        print("credentials not found, check .env", file=sys.stderr)
    except ClientError as e:
        print(f"upload failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"unexpected error: {e}", file=sys.stderr)
    return False


def main():
    local_path = input("local file path: ").strip()
    bucket = input("bucket name: ").strip()
    object_key = input("object key: ").strip()

    sys.exit(0 if upload_file(local_path, bucket, object_key) else 1)


if __name__ == "__main__":
    main()