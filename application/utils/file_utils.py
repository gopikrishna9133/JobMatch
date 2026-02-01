import secrets

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def random_filename(original_name: str) -> str:
    """Generate a random filename while preserving file extension."""
    ext = original_name.rsplit(".", 1)[1].lower()
    return f"{secrets.token_hex(8)}.{ext}"
