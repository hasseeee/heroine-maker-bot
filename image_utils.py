# image_utils.py
import os
import random

def get_random_image_url(base_url: str, images_dir: str = "images") -> str | None:
    """
    imagesディレクトリからランダムな画像ファイルを選び、
    指定されたbase_urlと組み合わせたURLを返す。
    """
    # 拡張子の指定
    valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")

    # 絶対パスに変換
    abs_images_dir = os.path.join(os.path.dirname(__file__), images_dir)

    # ファイルリスト取得
    image_files = [
        f for f in os.listdir(abs_images_dir)
        if f.lower().endswith(valid_extensions)
    ]

    if not image_files:
        return None

    chosen_image = random.choice(image_files)
    return f"{base_url}/images/{chosen_image}"
