import os
import zipfile
from configparser import ConfigParser
from pathlib import Path

import requests
from requests.exceptions import InvalidURL

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
        if not self.bnc.exists():
            try:
                r = requests.get(self.bnc_url, stream=True)
                with self.bnc.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            except InvalidURL:
                print("URL needs to be updated")

    def unzip(self):
        try:
            bnc_zip = zipfile.ZipFile(str(self.bnc), "r")
            current_dir = str(self.download_to)
            bnc_zip.extractall(current_dir)
            for f1 in bnc_zip.namelist():
                inner_file = self.download_to.joinpath(f1)
                if f1.endswith(".zip"):
                    inner_zip = zipfile.ZipFile(str(inner_file), "r")
                    inner_zip.extractall(current_dir)
        except zipfile.BadZipFile:
            print("This is not zip")

    def download_with_unzip(self):
        self.download()
        self.unzip()
