from os import cpu_count
from lxml import etree
from utils import exe_time
from configparser import ConfigParser, ExtendedInterpolation
import os
from pprint import pprint


cfg = ConfigParser(interpolation=ExtendedInterpolation())
cfg.read("config.ini")

namespace = cfg.get("reader", "xml_namespace")
corpus = cfg.get("reader", "corpus")

# @exe_time
def read(where):
    return etree.parse(where)


# def get_id(node):
#     return node.attrib.get(namespace + "id")


def get_all_xml(corpus):
    xmlfiles = []
    for root, dirs, filenames in os.walk(corpus):
        for filename in filenames:
            basename, extension = os.path.splitext(filename)
            if extension == ".xml":
                xmlfiles.append(os.path.join(root, filename))
    return xmlfiles


def _get_written_or_spoken_corpus_filenames(signature, xmlfiles):

    return [filename for filename in xmlfiles if signature in open(filename).read()]


@exe_time
def get_written_corpus(xmlfiles):
    return _get_written_or_spoken_corpus_filenames("<wtext", xmlfiles)


@exe_time
def get_spoken_corpus(xmlfiles):
    return _get_written_or_spoken_corpus_filenames("<stext", xmlfiles)


# get information
def get_title(tree):
    return tree.xpath("teiHeader/fileDesc/titleStmt/title")[0].text


if __name__ == "__main__":
    where = "data/written_test.xml"
    tree = read(where)
    xmlfiles = get_all_xml(corpus)
    print(get_title(tree))
    print(len(xmlfiles))
    s_corpus = get_spoken_corpus(xmlfiles)
    w_corpus = get_written_corpus(xmlfiles)
    pprint(len(s_corpus))
    pprint(len(w_corpus))
