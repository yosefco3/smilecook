import os
import uuid
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
from PIL import Image
from extensions import cache


def hash_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)


def generate_token(email, salt=None):
    serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
    return serializer.dumps(email, salt=salt)


def verify_token(token, max_age=30 * 60 * 60, salt=None):
    serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
    try:
        email = serializer.loads(token, max_age=max_age, salt=salt)
    except Exception as e:
        return False
    return email


def save_image(image, folder):
    if folder == "recipes":
        folder = os.environ.get("UPLOAD_RECIPES_FOLDER")
    if folder == "avatars":
        folder = os.environ.get("UPLOAD_AVATARS_FOLDER")
    filename = secure_filename(image.filename)
    filename = f"{uuid.uuid4()}.{filename.split('.')[1].lower()}"
    image.save(os.path.join(folder, filename))
    filename = compress_image(filename=filename, folder=folder)
    return filename


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compress_image(filename, folder):
    file_path = os.path.join(folder, filename)
    image = Image.open(file_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    if max(image.width, image.height) > 1600:
        maxsize = (1600, 1600)
        image.thumbnail(maxsize, Image.ANTIALIAS)
    compressed_filename = f"{uuid.uuid4()}.jpg"
    compressed_file_path = os.path.join(folder, compressed_filename)
    image.save(compressed_file_path, optimize=True, quality=80)
    original_size = os.stat(file_path).st_size
    compressed_size = os.stat(compressed_file_path).st_size
    percentage = round((original_size - compressed_size) / original_size * 100)
    print(
        f"the file size reduced by {percentage}% from {original_size} to {compressed_size}"
    )
    os.remove(file_path)
    return compressed_filename


def clear_cache(key_prefix):
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)

