import re
from abc import abstractmethod
from operator import itemgetter

from denite.source.base import Base  # pylint: disable=locally-disabled, import-error
from denite_gtags import GtagsBase  # pylint: disable=locally-disabled, wrong-import-position

GREP_HEADER_SYNTAX = (
    'syntax match deniteSource_grepHeader '
    r'/\v[^:]*:\d+(:\d+)? / '
    'contained keepend')

GREP_FILE_SYNTAX = (
    'syntax match deniteSource_grepFile '
    r'/[^:]*:/ '
    'contained containedin=deniteSource_grepHeader '
    'nextgroup=deniteSource_grepLineNR')
GREP_FILE_HIGHLIGHT = 'highlight default link deniteSource_grepFile Comment'

GREP_LINE_SYNTAX = (
    'syntax match deniteSource_grepLineNR '
    r'/\d\+\(:\d\+\)\?/ '
    'contained containedin=deniteSource_grepHeader')
GREP_LINE_HIGHLIGHT = 'highlight default link deniteSource_grepLineNR LineNR'

GREP_PATTERNS_HIGHLIGHT = 'highlight default link deniteGrepPatterns Function'


class TagsBase(GtagsBase):

    TAG_PATTERN = re.compile('([^\t]+)\t(\\d+)\t(.*)')

    def highlight(self):
        self.vim.command(GREP_HEADER_SYNTAX)
        self.vim.command(GREP_FILE_SYNTAX)
        self.vim.command(GREP_FILE_HIGHLIGHT)
        self.vim.command(GREP_LINE_SYNTAX)
        self.vim.command(GREP_LINE_HIGHLIGHT)
        self.vim.command(GREP_PATTERNS_HIGHLIGHT)

    def define_syntax(self):
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteSource_grepHeader,deniteMatchedRange contained')

    def convert_to_candidates(self, tags):
        candidates = []
        for tag in tags:
            path, line, text = cls._parse_tag(tag)
            col = text.find(self.word) + 1 if self.word else 0

            candidates.append({
                'word': text,
                'action__path': path,
                'action__line': line,
                'action_text': text,
                'action__col': col,
                'abbr': f'{path}:{line}:{col} {text}',
            })

        return candidates

    @classmethod
    def _parse_tag(cls, tag):
        match = cls.TAG_PATTERN.match(tag)
        return match.groups()
