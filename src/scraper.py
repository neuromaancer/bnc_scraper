from lxml import etree
from utils import exetime
from configparser import ConfigParser, ExtendedInterpolation
import os
from collections import namedtuple
from enum import Enum
import operator


cfg = ConfigParser(interpolation=ExtendedInterpolation())
cfg.read("config.ini")

namespace = cfg.get("reader", "xml_namespace")
corpus = cfg.get("reader", "corpus")


class QType(Enum):
    WHY = "why"
    WHEN = "when"
    WHAT = "what"
    WHERE = "where"
    WHICH = "which"
    HOW = "how"
    OTHER = ""


# @exetime
def read(where):
    return etree.parse(where)


def get_id(node):
    return node.attrib.get(f"{namespace}id")


def get_all_xml(corpus):
    xmlfiles = []
    try:
        check(corpus)
        for root, dirs, filenames in os.walk(corpus):
            for filename in filenames:
                basename, extension = os.path.splitext(filename)
                if extension == ".xml":
                    xmlfiles.append(os.path.join(root, filename))
        return xmlfiles
    except FileNotFoundError:
        pass


def _get_written_or_spoken_corpus_filenames(signature, xmlfiles):
    return [filename for filename in xmlfiles if signature in open(filename).read()]


@exetime
def get_written_corpus(xmlfiles):
    return _get_written_or_spoken_corpus_filenames("<wtext", xmlfiles)


@exetime
def get_spoken_corpus(xmlfiles):
    return _get_written_or_spoken_corpus_filenames("<stext", xmlfiles)


# get information
def get_title(tree):
    return tree.xpath("teiHeader/fileDesc/titleStmt/title")[0].text


def remove_ns(str_):
    return str_.replace(namespace, "")


def _pretty(d):
    for key, value in d.items():
        print(f"{remove_ns(key)}: {value}")


# stext
def print_persons(tree):
    persons = tree.xpath("teiHeader/profileDesc/particDesc/person")
    for person in persons:
        print("+" * 20)
        _pretty(person.attrib)
        for item in person:
            print(f"{item.tag}: {item.text}")


def get_words(xmlelement):
    return [
        word_tag.strip()
        for word_tag in xmlelement.itertext()
        if word_tag.strip().lower() is not ""
    ]


# stext
def get_utterances(tree):
    u_elems = tree.xpath("stext/u")
    utterances = []
    len_sentences = 0
    for u in u_elems:
        who = u.attrib["who"]
        u_l = {}
        for s in u.xpath("s"):
            n = int(s.attrib["n"])
            len_sentences = max(len_sentences, n)
            u_l[n] = get_words(s)
        u = namedtuple("u", ["who", "u_l"])
        utterances.append(u(who, u_l))
    return utterances, len_sentences


# stext
def get_questions(utterances):
    q_pairs = []
    for idx, u in enumerate(utterances):
        q_pairs.extend((idx, n, s) for n, s in u.u_l.items() if "?" in s)
    return q_pairs


# stext
def get_utterances_by_pairs(pairs, utterances):
    utters = []
    for idx, u in enumerate(utterances):
        if idx in map(operator.itemgetter(1), pairs):
            print(f"{u.who}: {u.u_l}")
        u = namedtuple("u", ["who", "u_l"])
        utters.append(u(u.who, u.u_l))
    return utters


# stext
def get_context(n, len_sentences, utterances, limit=5):
    r = min(n + limit, len_sentences)
    l = max(n - limit, 0)
    return get_sentences(list(range(l, r + 1)), utterances)


# stext
def get_questions_by_type(questions, q_type):
    return [(idx, n, s) for idx, n, s in questions if q_type in s]


# stext
def get_sentences(nums, utterances):
    sentences = []
    for u in utterances:
        sentences.extend((n, s) for n, s in u.u_l.items() if n in nums)
    return sentences


if __name__ == "__main__":
    where = "data/spoken_test.xml"
    tree = read(where)
    xmlfiles = get_all_xml(corpus)
    utterances, len_sentences = get_utterances(tree)
    # print("_______________", len_sentences)
    # questions = get_questions(utterances)
    # print(questions)
    # pprint(get_utterances_by_pairs(questions, utterances))
    #
    # print(context)

    # why = QType.WHY
    # questions = get_questions_by_type(questions, why)
    # print(type(questions))
    # print(questions)
    # num_ques = questions[0][1]
    # context = get_context(num_ques, len_sentences, utterances)
    # print(context)

    #######
    print_persons(tree)
