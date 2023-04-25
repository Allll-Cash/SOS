import io

from minio import Minio

from studreply import settings


def make_client():
    cli = Minio(
        settings.MINIO_HOST,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )
    cli.make_bucket(settings.MINIO_BUCKET_NAME)
    return cli


client = make_client()


def write_bytes(data: bytes, name: str):
    client.put_object(settings.MINIO_BUCKET_NAME, name, io.BytesIO(data), len(data))


def get_bytes(name: str) -> bytes:
    try:
        return client.get_object(settings.MINIO_BUCKET_NAME, name).data
    except Exception as e:
        print(e.with_traceback(None))
        return b''


def delete_file(name: str):
    try:
        client.remove_object(settings.MINIO_BUCKET_NAME, name)
    except Exception as e:
        print(e.with_traceback(None))
