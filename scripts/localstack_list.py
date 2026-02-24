"""List and upload to LocalStack S3."""

from __future__ import annotations

from pathlib import Path

import typer
from boto3 import client as boto_client
from botocore.config import Config

app = typer.Typer(name="localstack")
# Host via Traefik: http://localstack.localhost. Devcontainer: set LOCALSTACK_ENDPOINT=http://host.docker.internal:4566
DEFAULT_ENDPOINT = "http://localstack.localhost"
DEFAULT_REGION = "eu-west-2"


def _s3_client(endpoint: str, region: str):
    config = Config(
        region_name=region,
        s3={"addressing_style": "path"},
        connect_timeout=5,
        read_timeout=60,
        retries={"mode": "adaptive", "max_attempts": 4},
    )
    return boto_client(
        "s3",
        endpoint_url=endpoint,
        config=config,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def _s3_tree(s3, bucket: str, prefix: str = "", indent: str = "") -> list[str]:
    lines = []
    paginator = s3.get_paginator("list_objects_v2")
    try:
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/")
    except s3.exceptions.NoSuchBucket:
        return [f"{indent}└── (bucket not found)"]

    prefixes_seen = set()
    objects_seen = set()

    for page in pages:
        for cp in page.get("CommonPrefixes", []):
            p = cp["Prefix"]
            if p in prefixes_seen:
                continue
            prefixes_seen.add(p)
            name = p.rstrip("/").split("/")[-1] + "/"
            lines.append(f"{indent}├── {name}")
            sub = _s3_tree(s3, bucket, p, indent + "│   ")
            lines.extend(sub)

        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            if key in objects_seen:
                continue
            objects_seen.add(key)
            name = key.split("/")[-1]
            size = obj.get("Size", 0)
            size_str = f" ({size} B)" if size else ""
            lines.append(f"{indent}├── {name}{size_str}")

    for i in range(len(lines) - 1, -1, -1):
        if "├──" in lines[i]:
            lines[i] = lines[i].replace("├──", "└──", 1)
            break
    return lines


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """LocalStack S3: list buckets, upload files, create buckets."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_buckets)


@app.command("list")
def list_buckets(
    endpoint: str = typer.Option(
        DEFAULT_ENDPOINT, "--endpoint", "-e", envvar="LOCALSTACK_ENDPOINT", help="LocalStack endpoint"
    ),
    region: str = typer.Option(
        DEFAULT_REGION, "--region", "-r", help="AWS region"),
) -> None:
    """List LocalStack S3 buckets and objects as ASCII tree."""
    s3 = _s3_client(endpoint, region)
    try:
        buckets = s3.list_buckets().get("Buckets", [])
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if not buckets:
        typer.echo("LocalStack S3\n└── (no buckets)")
        return

    lines = ["LocalStack S3", "│"]
    for i, b in enumerate(buckets):
        name = b["Name"]
        is_last = i == len(buckets) - 1
        branch = "└──" if is_last else "├──"
        lines.append(f"{branch} {name}/")
        sub_indent = "    " if is_last else "│   "
        lines.extend(_s3_tree(s3, name, "", sub_indent))
    typer.echo("\n".join(lines))


def _create_bucket_params(bucket: str, region: str) -> dict:
    params: dict = {"Bucket": bucket}
    if region != "us-east-1":
        params["CreateBucketConfiguration"] = {"LocationConstraint": region}
    return params


def create_bucket(
    bucket: str = typer.Argument(..., help="Bucket name"),
    endpoint: str = typer.Option(
        DEFAULT_ENDPOINT, "--endpoint", "-e", envvar="LOCALSTACK_ENDPOINT", help="LocalStack endpoint"
    ),
    region: str = typer.Option(
        DEFAULT_REGION, "--region", "-r", help="AWS region"),
) -> None:
    """Create an S3 bucket in LocalStack."""
    s3 = _s3_client(endpoint, region)
    try:
        s3.create_bucket(**_create_bucket_params(bucket, region))
        typer.echo(f"Created bucket {bucket}")
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in ("BucketAlreadyExists", "BucketAlreadyOwnedByYou"):
            typer.echo(f"Bucket {bucket} already exists")
        else:
            raise


@app.command()
def upload(
    path: Path = typer.Argument(...,
                                help="File or folder to upload", path_type=Path),
    bucket: str = typer.Argument(..., help="S3 bucket name"),
    prefix: str = typer.Option(
        "", "--prefix", "-p", help="S3 key prefix (folder path in bucket)"),
    endpoint: str = typer.Option(
        DEFAULT_ENDPOINT, "--endpoint", "-e", envvar="LOCALSTACK_ENDPOINT", help="LocalStack endpoint"
    ),
    region: str = typer.Option(
        DEFAULT_REGION, "--region", "-r", help="AWS region"),
    create_bucket: bool = typer.Option(
        True, "--create-bucket/--no-create-bucket", help="Create bucket if missing"),
) -> None:
    """Upload a file or folder to LocalStack S3."""
    path = path.resolve()
    if not path.exists():
        typer.echo(f"Error: {path} does not exist", err=True)
        raise typer.Exit(1)

    s3 = _s3_client(endpoint, region)

    if create_bucket:
        buckets = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}
        if bucket not in buckets:
            s3.create_bucket(**_create_bucket_params(bucket, region))
            typer.echo(f"Created bucket {bucket}")

    prefix = prefix.rstrip("/") + "/" if prefix else ""

    if path.is_file():
        key = f"{prefix}{path.name}"
        s3.upload_file(str(path), bucket, key)
        typer.echo(f"Uploaded {path} -> s3://{bucket}/{key}")
    else:
        for f in path.rglob("*"):
            if f.is_file():
                rel = f.relative_to(path)
                key = f"{prefix}{rel.as_posix()}"
                s3.upload_file(str(f), bucket, key)
                typer.echo(f"  {rel} -> s3://{bucket}/{key}")


@app.command("rm")
def remove(
    bucket: str = typer.Argument(..., help="S3 bucket name"),
    key: str = typer.Argument(..., help="S3 object key (path in bucket)"),
    endpoint: str = typer.Option(
        DEFAULT_ENDPOINT, "--endpoint", "-e", envvar="LOCALSTACK_ENDPOINT", help="LocalStack endpoint"
    ),
    region: str = typer.Option(
        DEFAULT_REGION, "--region", "-r", help="AWS region"),
) -> None:
    """Remove a file from LocalStack S3."""
    s3 = _s3_client(endpoint, region)
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        typer.echo(f"Deleted s3://{bucket}/{key}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
