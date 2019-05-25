import re
from abc import abstractmethod
from operator import itemgetter

from denite.source.base import Base  # pylint: disable=locally-disabled, import-error
from denite_gtags import GtagsBase  # pylint: disable=locally-disabled, wrong-import-position


class TagsBase(GtagsBase):

    TAG_PATTERN = re.compile('([^\t]+)\t(\\d+)\t(.*)')

    @classmethod
    def convert_to_candidates(cls, tags):
        candidates = []
        max_name_width = 0
        for tag in tags:
            path, line, text = cls._parse_tag(tag)
            col = text.find(text) - 1

            if len(path) > max_name_width:
                max_name_width = len(path)

            candidates.append({
                'word': text,
                'action__path': path,
                'action__line': line,
                'action__text': text,
                'action__col': col,
            })

        for cand in candidates:
            cand['abbr'] = '{action__path:<{width}} {action__line:<4} {word}'.format(width=max_name_width, **cand)

        candidates.sort(key=itemgetter('action__text'))
        return candidates

    @classmethod
    def _parse_tag(cls, tag):
        match = cls.TAG_PATTERN.match(tag)
        return match.groups()
