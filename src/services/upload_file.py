import cloudinary
import cloudinary.uploader

from src.config.config import settings


class CloudinaryService:
    """
    Service for managing file uploads to Cloudinary.

    Handles interaction with the Cloudinary API for file storage and retrieval.
    """

    def __init__(self):
        """
        Initialize the Cloudinary configuration with credentials from application settings.
        """
        cloudinary.config(
            cloud_name=settings.CLD_NAME,
            api_key=settings.CLD_API_KEY,
            api_secret=settings.CLD_API_SECRET,
            secure=True,
        )

    async def upload_image(self, file, public_id: str = None) -> dict:
        """
        Upload an image file to Cloudinary.

        Args:
            file: File object to upload
            public_id: Optional custom public ID for the image

        Returns:
            dict: Upload response from Cloudinary containing URLs and metadata
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, folder="avatars")
        return r

    async def delete_image(self, public_id: str) -> dict:
        """
        Delete an image from Cloudinary by its public ID.

        Args:
            public_id: Public ID of the image to delete

        Returns:
            dict: Delete response from Cloudinary
        """
        r = cloudinary.uploader.destroy(public_id)
        return r
