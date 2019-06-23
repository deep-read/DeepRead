"""
Script used to download sample book covers from google images

You will need to download the chrome driver:
https://sites.google.com/a/chromium.org/chromedriver/downloads

Ensure you download the chrome driver that is compatible with your chrome
version
"""
from pathlib import Path

from google_images_download import google_images_download

OUT_DIR = './data/book_covers'

if not Path(OUT_DIR).is_dir():
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

response = google_images_download.googleimagesdownload()
response.download(
    {
        'keywords': 'book covers',
        'limit': 400,
        'chromedriver': './chromedriver',
        'output_directory': OUT_DIR,
        'no_directory': True,
    }
)
