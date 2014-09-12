# -*- coding: utf-8 -*-

import re
import os.path


SCRIPT_ROOT = os.path.abspath(os.path.dirname(__file__))
ABSOLUTE_PATH_TO_FILE_WITH_ERRORS = os.path.join(SCRIPT_ROOT, 'errors.txt')


class Error:
    def __init__(self, regexp, translation, linedetector = None):
        self.regexp = re.sub(r'\\{\d+\\}', '(.+)', re.escape(regexp))
        self.translation = translation
        self.locals_dict = {}
        if linedetector:
            # should create a function 'detect_error(error_msg, code_line)'
            exec(linedetector, self.locals_dict)

    def is_matched(self, error_msg, code_line):
        if 'detect_error' in self.locals_dict:
            return bool(re.match(self.regexp, error_msg)) and self.locals_dict['detect_error'](error_msg, code_line)
        else:
            return bool(re.match(self.regexp, error_msg))

    def get_translation(self, error_msg):
        return self.translation.format(*re.match(self.regexp, error_msg).groups())

    def __unicode__(self):
        return 'Error({0}, {1})'.format(self.regexp, self.translation)


errors = []


def load_error_information():
    global errors

    delimiters = set(['Regexp:', 'Translation:', 'LineDetector:'])

    curParts = []
    curDelimiter = None

    # fucking nonlocal variable in Python 2
    curError = [{}]

    def processRecord():
        # nonlocal curError
        if curDelimiter == 'Regexp:':
            curError[0]['regexp'] = '\n'.join(curParts).strip()
        elif curDelimiter == 'Translation:':
            curError[0]['translation'] = '<br>'.join([i for i in curParts if i]).strip()
        elif curDelimiter == 'LineDetector:':
            curError[0]['linedetector'] = '\n'.join(curParts)

        if 'translation' in curError[0]:
            errors.append(Error(**curError[0]))
            curError[0] = {}

    for line in open(ABSOLUTE_PATH_TO_FILE_WITH_ERRORS, encoding="utf-8"):
        # only strip TRAILING spaces and not leading spaces
        line = line.rstrip()

        # comments are denoted by a leading '//', so ignore those lines.
        # Note that I don't use '#' as the comment token since sometimes I
        # want to include Python comments in the skeleton code.
        if line.startswith('//'):
            continue

        if line in delimiters:
            processRecord()
            curDelimiter = line
            curParts = []
        else:
            curParts.append(line)

    # don't forget to process the FINAL record
    processRecord()


def get_error_explanation(error_msg, code_line):
    for error in errors:
        if error.is_matched(error_msg, code_line):
            explanation = error.get_translation(error_msg)
            return explanation

    return None


load_error_information()
