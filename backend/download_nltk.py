import os
import nltk

def download_nltk_packages():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "static_data/nltk_data")
    nltk.download("punkt_tab", download_dir=download_dir)
    nltk.download("stopwords", download_dir=download_dir)
