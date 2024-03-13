from . import downloader
import logging
import os
from configparser import ConfigParser, ExtendedInterpolation

logging.getLogger(__name__).addHandler(logging.NullHandler())


cfg = ConfigParser(interpolation=ExtendedInterpolation())
cfg.read("config.ini")

namespace = cfg.get("reader", "xml_namespace")
corpus = cfg.get("reader", "corpus")


def check(corpus):
    if not os.path.exists(corpus):
        raise FileNotFoundError
