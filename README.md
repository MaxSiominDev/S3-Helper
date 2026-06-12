# S3-Helper

A small set of CLI scripts for working with S3-compatible storage (Yandex Object Storage, AWS S3, etc.). Supports uploading/downloading individual files and entire folders with a progress bar

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the example config and fill in your keys:

```bash
cp .env.example .env
```

`.env`:

```
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
S3_ENDPOINT_URL=https://storage.yandexcloud.net
```

All scripts are interactive - they ask for parameters via prompts

## Scripts

### Single file

**Download a file:**

```bash
python download_from_s3.py
```
```
bucket: my-bucket
object key: photos/cat.jpg
destination [.]: ./downloads
```

**Upload a file:**

```bash
python upload_to_s3.py
```
```
local file path: ./cat.jpg
bucket name: my-bucket
object key: photos/cat.jpg
```

### Entire folder / bucket

**Download a folder (or the whole bucket) to your machine** - recursive, preserving structure:

```bash
python download_folder_from_s3.py
```
```
bucket: my-bucket
prefix (folder, empty for whole bucket): photos
destination [.]: .
```

Downloads `my-bucket/photos/...` into `./photos/...`. Empty prefix = the whole bucket

**Upload a folder to the bucket** — recursive:

```bash
python upload_folder_to_s3.py
```
```
local folder path: ./photos
bucket name: my-bucket
prefix (folder in bucket, empty for root): photos
```

Uploads everything under `./photos` into `my-bucket/photos/...`. Empty prefix = bucket root

### Round trip to the same location

To download `bucket/folder` and put it back in the exact same place, use the same prefix:

```
# download
bucket=my-bucket  prefix=photos   -> files in ./photos/...
# upload back
local=./photos  bucket=my-bucket  prefix=photos
```

## CI

`.github/workflows/ci.yml` runs on every push/PR to `main`:

- installs dependencies from `requirements.txt`;
- compiles all scripts (`py_compile`) on Python 3.14;
- lints with `ruff`
