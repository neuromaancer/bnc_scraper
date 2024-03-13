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

    def unzip(self):
        try:
            rprint(f"Unzipping {self.bnc}")
            with zipfile.ZipFile(str(self.bnc), "r") as bnc_zip:
                bnc_zip.extractall(path=str(self.download_to))
                rprint("Unzip successful!")
        except zipfile.BadZipFile:
            rprint("This is not a zip file")

    def download_with_unzip(self):
        self.download()
        self.unzip()


if __name__ == "__main__":
    bnc_url = cfg.get("download", "bnc_url")
    download_to = cfg.get("download", "download_to")
    downloader = Downloader(bnc_url, download_to)
    downloader.download_with_unzip()
