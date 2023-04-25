import io

from minio import Minio, S3Error

from studreply import settings


class MinioAdapter:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_HOST,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        try:
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)
        except S3Error:
            ...

    def put_object(self, name: str, data: bytes):
        self.client.put_object(settings.MINIO_BUCKET_NAME, name, io.BytesIO(data), len(data))

    def get_object(self, name: str) -> bytes:
        return self.client.get_object(settings.MINIO_BUCKET_NAME, name).data

    def remove_object(self, name: str):
        try:
            self.client.remove_object(settings.MINIO_BUCKET_NAME, name)
        except S3Error:
            ...


adapter = MinioAdapter()
