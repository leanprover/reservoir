import os
import hmac
import hashlib
import requests
from typing import Mapping
from datetime import datetime, timezone
from urllib.parse import urlparse, quote
from utils.core import filehash

# R2 client code adapted from https://github.com/fayharinn/R2-Client

def hmac_sha256(key: bytes, content: bytes):
  return hmac.new(key, content, hashlib.sha256).digest()

def aws4_signing_key(key: str, date: str, region: str, service: str):
  k_date = hmac_sha256(f"AWS4{key}".encode(), date.encode())
  k_region = hmac_sha256(k_date, region.encode())
  k_service = hmac_sha256(k_region, service.encode())
  k_signing = hmac_sha256(k_service, 'aws4_request'.encode())
  return k_signing

def aws4_uri_encode(string: str):
  return quote(string)

def aws4_headers(
    method: str, url: str, service: str,
    access_key_id: str, secret_access_key: str,
    payload_hash: str, region: str = 'auto',
    params: Mapping[str,str] = {}, headers: Mapping[str, str] = {}):
  url_parts = urlparse(url)
  host = str(url_parts.hostname) if url_parts.port is None else f"{url_parts.hostname}:{url_parts.port}"
  canonical_uri = aws4_uri_encode(url_parts.path)
  now = datetime.now(timezone.utc)
  amz_date = now.strftime('%Y%m%dT%H%M%SZ')
  date_stamp = now.strftime('%Y%m%d')
  algorithm = 'AWS4-HMAC-SHA256'
  headers = {k.lower(): v.strip() for k, v in headers.items()}
  headers['host'] = host
  headers['x-amz-content-sha256'] = payload_hash
  headers['x-amz-date'] = amz_date
  canonical_headers = ''.join(f"{h}:{v}\n" for h, v in headers.items())
  signed_headers = ";".join(headers.keys())
  canonical_query = '&'.join(f"{aws4_uri_encode(p)}={aws4_uri_encode(v)}" for p, v in params)
  canonical_request = f"{method}\n{canonical_uri}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
  hashed_request = hashlib.sha256(canonical_request.encode()).hexdigest()
  credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
  string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_request}"
  signing_key = aws4_signing_key(secret_access_key, date_stamp, region, service)
  signature = hmac_sha256(signing_key, string_to_sign.encode()).hex()
  authorization = f"{algorithm} Credential={access_key_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
  headers['authorization'] = authorization
  return headers

S3_SESSION = requests.Session()
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", '').rstrip('/')
S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID', '')
S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY', '')
S3_ENABLED = S3_ENDPOINT != '' and S3_ACCESS_KEY_ID != '' and S3_SECRET_ACCESS_KEY != ''
def upload_build(path: str, size: int | None = None, hash: str | None = None):
  if not S3_ENABLED:
    raise RuntimeError("No cloud storage configured")
  method = 'PUT'
  if size is None: size = os.path.getsize(path)
  if hash is None: hash = filehash(path)
  url = f"{S3_ENDPOINT}/b1/{hash}.barrel"
  headers = aws4_headers(method, url, 's3', S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, hash)
  headers['content-length'] = str(size)
  headers['content-type'] = "application/vnd.reservoir.barrel+gzip"
  with open(path, 'rb') as f:
    resp = S3_SESSION.request(method, url, data=f, headers=headers)
  if resp.status_code != 200:
    raise RuntimeError(f"Failed to upload build ({resp.status_code}): {resp.text}")
