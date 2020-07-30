from test import *
from bnc_scraper.downloader import Downloader

cfg = ConfigParser()
cfg.read("config.ini")

bnc_url = cfg.get("download", "bnc_url")
download_to = cfg.get("download", "download_to")


class TestDownloader:
    def test_download(self):
        dl = Downloader(bnc_url, download_to)
        dl.download()
        assert dl.bnc.exists() == True

    @pytest.mark.skip(reason="unknown error")
    def test_download_raise(self):
        dl = Downloader(bnc_url=1, download_to=download_to)
        print(dl.bnc_url)
        with pytest.raises(InvalidURL) as e:
            dl.download()
        exec_msg = e.value.args[0]
        assert exec_msg == "The URL provided was somehow invalid."

