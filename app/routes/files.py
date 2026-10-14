import uuid

import boto3
from botocore.config import Config
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings

router = APIRouter(prefix="/files", tags=["files"])

BUCKET = settings.s3_bucket_name

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    config=Config(signature_version="s3v4"),
)


@router.post("/")
def upload_file(file: UploadFile = File(...)) -> dict:
    """
    Метод upload_fileobj() отправляет содержимое файлового объекта в S3
    и поддерживает multipart upload для больших файлов
    :param file:
    :return dict:
    """
    allowed_types = {
        "image/jpeg",
        "image/png",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG are allowed",
        )

    # Дополнительный лимит на размер файла
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds 5 MB",
        )

    extension = (
        ".jpg" if file.content_type == "image/jpeg"
        else ".png"
    )

    key = f"uploads/{uuid.uuid4()}{extension}"

    s3.upload_fileobj(
        file.file,
        BUCKET,
        key,
        ExtraArgs={
            "ContentType": file.content_type
        },
    )

    return {
        "message": "File uploaded",
        "key": key,
    }
