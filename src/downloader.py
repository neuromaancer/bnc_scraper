import os
import requests
import zipfile
from configparser import ConfigParser
from pathlib import Path
import time
from rich import print as rprint

cfg = ConfigParser()
cfg.read("config.ini")


class Downloader:
    def __init__(self, bnc_url, download_to) -> None:
        self.bnc_url = bnc_url
        self.download_to = Path(download_to)

    @property
    def bnc(self):
        if not self.download_to.exists():
            os.makedirs(self.download_to)
        return Path(self.download_to / "bnc.zip")

    def download(self):
        if self.bnc.exists():
            return
        try:
            self._extracted_from_download()
        except requests.exceptions.InvalidURL:
            rprint("URL needs to be updated")

    # TODO Rename this here and in `download`
    def _extracted_from_download(self):
        start_time = time.time()  # Start timing
        rprint("Downloading...")
        r = requests.get(self.bnc_url, stream=True)
        with self.bnc.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        end_time = time.time()  # End timing
        file_size = self.bnc.stat().st_size / (1024 * 1024)
        rprint(
            f"Download completed in {end_time - start_time:.2f} seconds. File size: {file_size:.2f} MB"
        )

    def unzip_recursive(self, zip_path, extract_to):
        """Recursive unzip function."""
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
                rprint(f"Extracted {zip_path} to {extract_to}")

            # Check for nested zip files
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    if file.endswith(".zip"):
                        file_path = os.path.join(root, file)
                        # Create a new folder for the nested zip based on its name (without the .zip extension)
                        nested_extract_to = os.path.join(
                            extract_to, os.path.splitext(file)[0]
                        )
                        os.makedirs(nested_extract_to, exist_ok=True)
                        # Recursively unzip
                        self.unzip_recursive(file_path, nested_extract_to)
                        # Optionally, remove the zip file after extraction
                        os.remove(file_path)

        except zipfile.BadZipFile:
            rprint(f"{zip_path} is not a zip file")

    def unzip(self):
        """Unzips the main zip file and any nested zip files."""
        rprint(f"Unzipping {self.bnc}")
        self.unzip_recursive(str(self.bnc), str(self.download_to))
        rprint("Unzip successful!")

    def download_with_unzip(self):
        self.download()
        self.unzip()


if __name__ == "__main__":
    bnc_url = cfg.get("download", "bnc_url")
    download_to = cfg.get("download", "download_to")
    downloader = Downloader(bnc_url, download_to)
    downloader.download_with_unzip()
