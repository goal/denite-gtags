import os
import subprocess
from abc import abstractmethod
from denite.source.base import Base  # pylint: disable=locally-disabled, import-error
import denite.util  # pylint: disable=locally-disabled, import-error


def get_subprocess_env(vim):
    """ Determine whether gen_tags gtags is in use, if so fit to its config.
    :returns: env

    """
    if vim.call("exists", "g:loaded_gentags#gtags"):
        if vim.call("eval", "g:loaded_gentags#gtags"):
            custom_env = os.environ.copy()
            custom_env["GTAGSROOT"] = vim.call("eval", "$GTAGSROOT")
            custom_env["GTAGSDBPATH"] = vim.call("eval", "$GTAGSDBPATH")
            return custom_env
    return None


class GtagsBase(Base):
    def gather_candidates(self, context):
        self.word = self._get_search_word(context)

        candidates = []
        for search_flags in self.get_search_flags():
            if self.word:
                search_flags += ['--', self.word]

            tags = self._exec_global(search_flags, context)
            candidates += self.convert_to_candidates(tags)

        return candidates

    @abstractmethod
    def get_search_flags(self):
        return [[]]

    @abstractmethod
    def convert_to_candidates(self):
        raise NotImplementedError()

    def _get_search_word(self, context):
        args_count = len(context['args'])
        if args_count > 0:
            return context['args'][0]

        return context['input']

    def _exec_global(self, search_args, context, input=None):
        command = ['global', '-q'] + search_args
        global_proc = subprocess.Popen(
            command,
            cwd=context['path'],
            universal_newlines=True,
            stdin=subprocess.PIPE if input else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=get_subprocess_env(self.vim))
        try:
            output, error = global_proc.communicate(input=input, timeout=15)
        except subprocess.TimeoutExpired:
            global_proc.kill()
            output, error = global_proc.communicate()
        global_exitcode = global_proc.returncode

        if global_exitcode != 0:
            self._print_global_error(global_exitcode, error)
            return []

        return [t for t in output.split('\n') if len(t) > 0]

    def _print_global_error(self, global_exitcode, error):
        if global_exitcode == 1:
            message = '[denite-gtags] Error: File does not exists'
        elif global_exitcode == 2:
            message = '[denite-gtags] Error: Invalid arguments\n{error}'
        elif global_exitcode == 3:
            message = '[denite-gtags] Error: GTAGS not found'
        elif global_exitcode == 126:
            message = f'[denite-gtags] Error: Permission denied\n{error}'
        elif global_exitcode == 127:
            message = '[denite-gtags] Error: \'global\' command not found'
        else:
            message = '[denite-gtags] Error: global command failed\n{error}'
        denite.util.error(self.vim, message)
