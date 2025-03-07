import io
from PIL import Image

# Allowed image formats
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png"}
MAX_FILE_SIZE_MB = 5  # Set maximum file size limit

def process_uploaded_image(uploaded_file) -> dict:
    """
    Process the uploaded file, validate its format, and extract MIME type & raw data.
    """
    try:
        # Check if file is uploaded
        if not uploaded_file:
            raise ValueError("No file uploaded.")

        # Validate file size (limit: 5MB)
        uploaded_file.seek(0, io.SEEK_END)  # Move to end of file
        file_size_mb = uploaded_file.tell() / (1024 * 1024)  # Convert bytes to MB
        uploaded_file.seek(0)  # Reset file pointer to start

        if file_size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"File size too large ({file_size_mb:.2f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB.")

        # Validate file format
        mime_type = uploaded_file.mimetype.lower()
        file_extension = uploaded_file.filename.rsplit(".", 1)[-1].lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file format: {file_extension}. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}.")

        # Load image to check integrity
        image = Image.open(uploaded_file)
        image.verify()  # Verifies if it's a valid image

        # Read file content and return metadata
        uploaded_file.seek(0)  # Reset file pointer
        return {"mime_type": mime_type, "data": uploaded_file.read()}

    except Exception as e:
        print(f"Image Processing Error: {str(e)}")
        return {"error": str(e)}
