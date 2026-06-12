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


def upload_folder(local_dir: str, bucket: str, prefix: str) -> bool:
    root = Path(local_dir)
    if not root.is_dir():
        print(f"'{local_dir}' is not a directory", file=sys.stderr)
        return False

    files = [p for p in root.rglob("*") if p.is_file()]
    if not files:
        print(f"no files found in '{local_dir}'", file=sys.stderr)
        return False

    s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)

    print(f"found {len(files)} file(s) in {root}")
    failed = 0
    for local_file in files:
        rel = local_file.relative_to(root).as_posix()
        object_key = f"{prefix}{rel}" if prefix else rel
        try:
            s3.upload_file(
                str(local_file), bucket, object_key, Callback=ProgressPercentage(local_file)
            )
        except NoCredentialsError:
            print("credentials not found, check .env", file=sys.stderr)
            return False
        except ClientError as e:
            print(f"upload failed for {object_key}: {e}", file=sys.stderr)
            failed += 1
        except Exception as e:
            print(f"unexpected error for {object_key}: {e}", file=sys.stderr)
            failed += 1

    if failed:
        print(f"completed with {failed} failure(s)", file=sys.stderr)
        return False

    print(f"upload complete: {root} -> s3://{bucket}/{prefix}")
    return True


def main():
    local_dir = input("local folder path: ").strip()
    bucket = input("bucket name: ").strip()
    prefix = input("prefix (folder in bucket, empty for root): ").strip()
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    sys.exit(0 if upload_folder(local_dir, bucket, prefix) else 1)


if __name__ == "__main__":
    main()
