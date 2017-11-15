from __future__ import division, print_function

import doctest
import inspect
import os
import re
import sys
import traceback


# The name of the plugin as it is displayed on the web interface. Note
# that this plugin handles both NFAs and Turing machines!
PLUGIN_NAME = "JFLAP (New)"


class StringError(Exception):
    """Exception thrown when parsing a malformed string literal."""
    pass


class JFLAPTestFileParseError(Exception):
    """Exception thrown when parsing a malformed JFLAP test file."""
    pass


# Keywords that may be used in the test file to identify bitstrings
# that should be either accepted or rejected by NFAs or Turing
# machines.
result_kwords = {"accepted": True,
                 "accepts": True,
                 "yes": True,
                 "good": True,
                 "ok": True,
                 "rejected": False,
                 "rejects": False,
                 "no": False,
                 "bad": False}


def len_lex(string):
    """Key function to sort a list of strings first by length and then
    lexicographically.

    >>> sorted(["b", "abc", "ca", "ac", "bb", "aaaa", ""], key=len_lex)
    ['', 'b', 'ac', 'bb', 'ca', 'abc', 'aaaa']
    """
    return len(string), string


def all_bitstrings(length):
    """Returns all bitstrings of at most the given length.

    This includes the empty bitstring. The bitstrings are returned as
    a generator, sorted first by length and then lexicographically.

    >>> list(all_bitstrings(-1))
    []
    >>> list(all_bitstrings(0))
    ['']
    >>> list(all_bitstrings(1))
    ['', '0', '1']
    >>> list(all_bitstrings(2))
    ['', '0', '1', '00', '01', '10', '11']
    >>> len(list(all_bitstrings(6))) == 2 ** 7 - 1
    True
    >>> sorted(list(all_bitstrings(6)), key=len_lex) == list(all_bitstrings(6))
    True
    """
    if length >= 0:
        yield ""
    current = "0"
    while len(current) <= length:
        yield current
        for j in range(len(current)):
            i = len(current) - 1 - j
            if current[i] == "0":
                current = current[:i] + "1" + "0" * j
                break
            elif i == 0:
                current = "0" * (len(current) + 1)


def split_with_quotes(string):
    r"""Splits a string on whitespace, allowing the use of single or double
    quotes for grouping.

    >>> split_with_quotes("foo bar baz quux")
    ['foo', 'bar', 'baz', 'quux']
    >>> split_with_quotes("  foo\t \nbar baz\vquux     ")
    ['foo', 'bar', 'baz', 'quux']
    >>> split_with_quotes("foo 'bar baz' quux")
    ['foo', 'bar baz', 'quux']
    >>> split_with_quotes("foo 'bar b'az ''quux")
    ['foo', 'bar b', 'az', '', 'quux']
    >>> split_with_quotes('''''""'""'"''"''')
    ['', '', '""', "''"]
    >>> split_with_quotes(r"foo 'b\'\\ar' baz")
    ['foo', "b'\\ar", 'baz']
    >>> split_with_quotes(r"foo 'bar\n' baz quux")
    Traceback (most recent call last):
        ...
    StringError: invalid backslash escape '\n' in single-quoted string literal in: foo 'bar\n' baz quux
    >>> split_with_quotes("foo ba'r baz quux")
    ['foo', 'ba', 'r baz quux']
    >>> split_with_quotes(r"foo \'bar\'' '\'baz 'qu\ux")
    ['foo', '\\', "bar'", "'baz ", 'qu\\ux']
    >>> split_with_quotes(r'foo "bar\'" baz')
    Traceback (most recent call last):
        ...
    StringError: invalid backslash escape "\'" in double-quoted string literal in: foo "bar\'" baz
    """
    groups = []
    current_group = ""
    quote = None
    backslash = False
    for char in string:
        if quote is None:
            if char == "'":
                quote = "'"
            elif char == '"':
                quote = '"'
            if char in "'\"" or char.isspace():
                if current_group:
                    groups.append(current_group)
                    current_group = ""
            else:
                current_group += char
        elif quote == "'":
            if char == "'" and not backslash:
                quote = None
                groups.append(current_group)
                current_group = ""
            elif char == "\\" and not backslash:
                backslash = True
            elif backslash and char not in "'\\":
                raise StringError("invalid backslash escape '\\{}' in"
                                  " single-quoted string literal in: {}"
                                  .format(char, string))
            else:
                current_group += char
                backslash = False
        elif quote == '"':
            if char == '"' and not backslash:
                quote = None
                groups.append(current_group)
                current_group = ""
            elif char == "\\" and not backslash:
                backslash = True
            elif backslash and char not in '"\\':
                raise StringError('invalid backslash escape "\\{}" in'
                                  " double-quoted string literal in: {}"
                                  .format(char, string))
            else:
                current_group += char
                backslash = False
        else:
            # We only ever assign "quote" to be None, "'", or '"'.
            # This branch should never be reached!
            raise AssertionError
    if current_group:
        groups.append(current_group)
    return groups


def result_to_str(should_accept):
    """Transforms an expected result from a boolean into a string (True
    for "accepted" and False for "rejected").
    """
    if should_accept:
        return "accepted"
    else:
        return "rejected"


def exception_name(e):
    """Returns the name of an exception, e.g. "ValueError".

    >>> try:
    ...     raise ValueError("uh oh")
    ... except Exception as e:
    ...     print(exception_name(e))
    ValueError
    """
    return type(e).__name__


def exception_linum(height=0):
    """Returns the line number of the last exception.

    Providing a nonzero height means a line number higher in the stack
    trace (further from the source of the exception) is reported.
    Negative numbers count from the top.

    >>> exec '''def foo():
    ...     raise ValueError("uh oh")
    ... try:
    ...     foo()
    ... except ValueError:
    ...     print(exception_linum())
    ...     print(exception_linum(height=1))'''
    2
    4
    """
    # Alternative way of accomplishing the same thing:
    # return traceback.extract_tb(sys.exc_info()[2])[-1 - height][1]
    return inspect.getinnerframes(sys.exc_info()[2])[-1 - height][2]


def parse_test_file_contents(contents):
    r"""Parses the contents of a JFLAP test file.

    The contents of the test file should be provided as a multiline
    string. This function will parse the string and return a
    dictionary mapping input strings to boolean values, with False
    meaning that the input should be rejected by the NFA or Turing
    machine and True meaning that the input should be accepted by the
    NFA or Turing machine.

    The test file may contain test cases and function definitions.
    Syntactically, a test case is a sequence of whitespace-delimited
    tokens on a single line. All whitespace is ignored, except to
    determine where to split the line into tokens. However, you may
    use double or single quotes to group tokens together. This way,
    you can include whitespace inside a single token. A token boundary
    always occurs directly before and after a pair of quotes. Note
    that you can also include quotes of the same type by escaping them
    with a backslash, and backslashes in the same way. Those are the
    only allowed backslash escapes. Note that backslash escapes are
    unnecessary except in quoted tokens.

    Test files may contain comments. If a line starts with an
    octothorpe (#), discounting leading whitespace, then it is
    ignored. If you wish for the first token to begin with an
    octothorpe, quote it. Note that there is no support for
    end-of-line comments. Comments must begin at the beginning of
    lines.

    All but the first and last tokens of a test case are ignored. You
    may use intermediate tokens to improve the appearance and
    readability of the test cases (for instance, by including an arrow
    "->"). The first token is the input string for the NFA or Turing
    machine, and the last token is a word identifying whether it
    should be accepted or rejected. The input string can contain any
    characters (other than, of course, newline characters), and the
    accept/reject word can be any prefix of any of the keys in
    "result_words", as long as it does not match two words with
    opposite meanings. (This is not possible with the current value of
    "result_words", but it might become possible if the dictionary is
    broadened in future.) Note that you can provide a test case for
    the empty string using an empty pair of quotes ("").

    If only one token is provided, it is assumed to be the input
    string and the accept/reject value of the test case is left
    undefined, to be determined by the "check" function or to default
    to "accept" if "check" is not defined. If no tokens are provided,
    then the line must be whitespace-only, and it is skipped.

    At any point in the test file, you may define a function of one
    argument called "check", a function of no arguments called
    "words", both, or neither. These are standard Python functions.
    You must use at least four-space indentation in function
    definitions, and they cannot contain any lines with only
    whitespace. In both "words" and "check", you will have access to
    the function "all_bitstrings" defined above.

    If you define "words", then it is called to obtain an iterable of
    input strings that will be used as test cases in addition to those
    explicitly specified in the file. These generated test cases will
    not have information about whether they should be rejected or
    accepted, so if you do not define "check" or also specify the test
    cases and their desired results explicitly in the test file, then
    they will default to "accept" for reasons of reverse
    compatibility.

    If you define "check", then it is called with any input strings
    for which you did not provide a result keyword, as well as any
    input strings generated by "words" for which a result keyword is
    not also provided in the explicit test cases, in order to
    determine the intended result for the input string (logical true
    meaning accept or and logical false meaning reject).

    This version of the function is completely reverse compatible with
    old-style test files, with the aid of a CSS-like "quirks mode".

    >>> def normalize(tests):
    ...     def key(item):
    ...         return len_lex(item[0])
    ...     for item in sorted(tests.items(), key=key):
    ...         print(item)

    >>> normalize(parse_test_file_contents('''
    ... 0
    ... 1
    ... 00
    ... 01 reject
    ... 10 reject
    ... 11'''))
    ('', True)
    ('0', True)
    ('1', True)
    ('00', True)
    ('01', False)
    ('10', False)
    ('11', True)

    >>> normalize(parse_test_file_contents(r'''
    ... foo should be accepted
    ... "" (the empty string) should be rejected
    ... # this is a comment
    ... 'string with spaces' -> ok
    ... 'weird\'" str\\ing' reject
    ... def words():
    ...     yield 'extra test case'
    ...     for word in all_bitstrings(2):
    ...         yield word
    ... "unspecified test case"
    ...           ???
    ... "# quoted comment"
    ... 0101 y
    ... def check(word):
    ...     # note, this is overridden for the empty string!
    ...     return len(word) % 2 == 0
    ... 'https://xkcd.com/859/ "("
    ... # you can actually have blank lines now!
    ...
    ... 1010 is TOTALLY REJECTED'''))
    ('', False)
    ('0', False)
    ('1', False)
    ('00', True)
    ('01', True)
    ('10', True)
    ('11', True)
    ('???', False)
    ('foo', True)
    ('0101', True)
    ('1010', False)
    ('extra test case', False)
    ('weird\'" str\\ing', False)
    ('# quoted comment', True)
    ('string with spaces', True)
    ('unspecified test case', False)
    ('https://xkcd.com/859/ "("', False)

    >>> parse_test_file_contents(r'''
    ... 10 reject
    ... 11 reject
    ... 11
    ... 10 accept''')
    Traceback (most recent call last):
        ...
    JFLAPTestFileParseError: test case on line 2 specifies that input string '10' should be rejected, but test case on line 5 specifies that it should be accepted

    >>> parse_test_file_contents(r'''
    ... 10 accept
    ... def words():
    ...     return ["a", "b, "c"]
    ... 01 reject''')
    Traceback (most recent call last):
        ...
    JFLAPTestFileParseError: syntax error in definition of 'words' on line 4: SyntaxError: invalid syntax

    >>> parse_test_file_contents(r'''
    ... 1010
    ... def check():
    ...     return True
    ... 0101 -> reject''')
    Traceback (most recent call last):
        ...
    JFLAPTestFileParseError: 'check' must be a function of one argument, but it is defined with 0 required arguments (on line 3)

    >>> parse_test_file_contents(r'''
    ... 1010
    ... def check(foo):
    ...     return bar
    ... 0101 -> reject''')
    Traceback (most recent call last):
        ...
    JFLAPTestFileParseError: error on line 4 while invoking check('1010'): NameError: global name 'bar' is not defined

    >>> parse_test_file_contents(r'''
    ... "ok test case" -> accept
    ... "malforme\d test case" -> reject''')
    Traceback (most recent call last):
        ...
    JFLAPTestFileParseError: malformed test case on line 3: invalid backslash escape "\d" in double-quoted string literal in: "malforme\d test case" -> reject
    """
    # First we define the dictionary from inputs to results that will
    # be returned at the end of this function.
    tests = {}
    # Now we check to see if the test file is an "old style" test
    # file, so that we can provide reverse compatibility. This is very
    # similar to "quirks mode" in browsers. It would be preferable, of
    # course, for the "new style" syntax to be backwards compatible
    # with the "old style" syntax, but this is not feasible because
    # the "old style" syntax requires that any blank line add the test
    # case specifying that the empty string is to be accepted.
    is_old_style = True
    for line in contents.splitlines():
        if not re.match(r"\s*\S*\s*(reject\s*)?$", line):
            is_old_style = False
            break
    # Now we actually parse the file contents.
    if is_old_style:
        for line in contents.splitlines():
            line = line.strip()
            should_reject = line.endswith("reject")
            if should_reject:
                line = line[:-len("reject")]
                line = line.rstrip()
                word = line
                tests[word] = False
            else:
                tests[line] = True
    else:
        # We define a dictionary with the same keys as "tests", but
        # with the values being the numbers of the lines on which the
        # respective inputs have test cases defined. This allows us to
        # provide a more useful error message when there are duplicate
        # definitions.
        test_linums = {}
        # Possible states are "standard" (reading manual test
        # specifications), "reading_words_definition" (reading the
        # definition of the "words" function), and
        # "reading_check_definition" (reading the definition of the
        # "check" function).
        state = "standard"
        # Lists of lines in the definitions of the "words" and "check"
        # functions.
        words_code_lines = []
        check_code_lines = []
        # Start line numbering from 1.
        for linum, line in enumerate(contents.splitlines(), 1):
            # Trim trailing whitespace. Note that we can't trim
            # leading whitespace, because this would break any
            # embedded Python function definitions.
            line = line.rstrip()
            if state == "reading_words_definition":
                if len(words_code_lines) >= 2:
                    body_line = words_code_lines[1]
                    indent_depth = len(body_line) - len(body_line.lstrip())
                    indent = re.escape(body_line[:indent_depth])
                else:
                    def_line = words_code_lines[0]
                    indent_depth = len(def_line) - len(def_line.lstrip())
                    indent = r"\s" * (indent_depth + 1)
                # We assume that function declarations have ended when
                # we find a line that isn't indented. But we allow
                # blank lines, even if they are not indented.
                if re.match(indent, line) or not line:
                    words_code_lines.append(line)
                else:
                    state = "standard"
            elif state == "reading_check_definition":
                if len(check_code_lines) >= 2:
                    body_line = check_code_lines[1]
                    indent_depth = len(body_line) - len(body_line.lstrip())
                    indent = re.escape(body_line[:indent_depth])
                else:
                    def_line = check_code_lines[0]
                    indent_depth = len(def_line) - len(def_line.lstrip())
                    indent = r"\s" * (indent_depth + 1)
                if re.match(indent, line) or not line:
                    check_code_lines.append(line)
                else:
                    state = "standard"
            # Skip empty lines and comments, but not inside function
            # definitions (that would mess up the line numbers
            # reported in error messages).
            if not line or line.lstrip().startswith("#"):
                continue
            if state == "standard":
                if re.match(r"\s*def words\(", line):
                    # Only allow one definition of each function.
                    if words_code_lines:
                        # If words_code_lines is non-empty, then we must
                        # have already run the "else" branch of this "if"
                        # statement at least once, we know that
                        # words_definition_linum will be defined.
                        error = ("duplicate definitions of 'words' on lines {}"
                                 " and {}"
                                 .format(words_definition_linum, linum))
                        raise JFLAPTestFileParseError(error)
                    else:
                        words_code_lines.append(line)
                        words_definition_linum = linum
                        state = "reading_words_definition"
                elif re.match(r"\s*def check\(", line):
                    if check_code_lines:
                        # If check_code_lines is non-empty, then we must
                        # have already run the "else" branch of this "if"
                        # statement at least once, we know that
                        # check_definition_linum will be defined.
                        error = ("duplicate definitions of 'check' on lines {}"
                                 " and {}"
                                 .format(check_definition_linum, linum))
                        raise JFLAPTestFileParseError(error)
                    else:
                        check_code_lines.append(line)
                        check_definition_linum = linum
                        state = "reading_check_definition"
                    continue
                else:
                    try:
                        groups = split_with_quotes(line)
                    except StringError as e:
                        error = ("malformed test case on line {}: {}"
                                 .format(linum, e.message))
                        raise JFLAPTestFileParseError(error)
                    if not groups:
                        # If we don't have any groups, the line must
                        # be whitespace-only or empty. But we skip
                        # such lines earlier, so this can't happen!
                        raise AssertionError
                    word = groups[0]
                    if len(groups) == 1:
                        if word not in tests:
                            tests[word] = None
                    else:
                        # The last token should be a prefix of one or
                        # more "reject" keywords or one or more
                        # "accept" keywords. If it's both or neither,
                        # we have a problem.
                        result_prefix = groups[-1].lower()
                        reject_kword_match = None
                        accept_kword_match = None
                        for result_kword, should_accept in result_kwords.items():
                            if result_kword.startswith(result_prefix):
                                if should_accept:
                                    accept_kword_match = result_kword
                                else:
                                    reject_kword_match = result_kword
                        if not (accept_kword_match or reject_kword_match):
                            error = ("result specifier '{}' on line {} does"
                                     " not match any of the valid result"
                                     " specifiers, which are: {}"
                                     .format(result_prefix, linum,
                                             ", ".join("'{}'".format(kword)
                                                       for kword in result_kwords.keys())))
                            raise JFLAPTestFileParseError(error)
                        elif accept_kword_match and reject_kword_match:
                            error = ("result specifier '{}' on line {} is"
                                     " ambiguous, could match either '{}'"
                                     " or '{}'"
                                     .format(result_prefix, linum,
                                             accept_kword_match,
                                             reject_kword_match))
                            raise JFLAPTestFileParseError(error)
                        else:
                            should_accept = result_kwords[accept_kword_match or
                                                          reject_kword_match]
                            # Use "is" because we're comparing
                            # singleton values.
                            if (tests.get(word, None) not in (None, should_accept)):
                                error = ("test case on line {} specifies that"
                                         " input string '{}' should be {}, but"
                                         " test case on line {} specifies that"
                                         " it should be {}"
                                         .format(test_linums[word],
                                                 word,
                                                 result_to_str(not should_accept),
                                                 linum,
                                                 result_to_str(should_accept)))
                                raise JFLAPTestFileParseError(error)
                            tests[word] = should_accept
                            test_linums[word] = linum
        # Using a custom namespace is the preferred way to extract a
        # declared variable from an 'exec' call.
        #
        # Note that this also has the effect of preventing the code in
        # the test file from reading from or writing to the actual
        # global or local namespaces of this script, which is good.
        #
        # We do, however, want to make "all_bitstrings" available to
        # the test file's inline functions (in particular, to
        # "words"), hence the initial value of "namespace".
        namespace = {"all_bitstrings": all_bitstrings,
                     # If there are test cases without explicit results
                     # defined, and "check" is not defined in the test
                     # file, then we want to set those test cases to
                     # "accept".
                     "check": lambda word: True}
        # If one of the lists is empty, then the corresponding call is
        # a no-op. There's no need to check first.
        try:
            exec "\n".join(words_code_lines) in namespace
        except SyntaxError as e:
            error = ("syntax error in definition of 'words' on line {}: {}: {}"
                     .format(words_definition_linum + (e.lineno - 1),
                             exception_name(e),
                             e.msg))
            raise JFLAPTestFileParseError(error)
        except Exception as e:
            error = ("error in definition of 'words' on line {}: {}: {}"
                     .format(words_definition_linum + (exception_linum() - 1),
                             exception_name(e),
                             e.msg))
            raise JFLAPTestFileParseError(error)
        try:
            exec "\n".join(check_code_lines) in namespace
        except SyntaxError as e:
            error = ("syntax error in definition of 'check' on line {}: {}: {}"
                     .format(check_definition_linum + (e.lineno - 1),
                             exception_name(e),
                             e.msg))
            raise JFLAPTestFileParseError(error)
        except Exception as e:
            error = ("error in definition of 'check' on line {}: {}: {}"
                     .format(check_definition_linum + (exception_linum() - 1),
                             exception_name(e),
                             e.msg))
            raise JFLAPTestFileParseError(error)
        if words_code_lines:
            words_fn = namespace["words"]
            required_arg_count = len(inspect.getargspec(words_fn).args)
            if required_arg_count != 0:
                error = ("'words' must be a function of no arguments, but"
                         " it is defined with {} required arguments"
                         " (on line {})"
                         .format(required_arg_count, words_definition_linum))
                raise JFLAPTestFileParseError(error)
            try:
                words = words_fn()
            except Exception as e:
                error = ("error on line {} while invoking words(): {}: {}"
                         .format(words_definition_linum + (exception_linum() - 1),
                                 exception_name(e),
                                 e.message))
                raise JFLAPTestFileParseError(error)
            for word in words:
                # Allow overriding "check" with manually specified
                # test cases for the input strings generated by
                # "words".
                if word not in tests:
                    tests[word] = None
        check_fn = namespace["check"]
        required_arg_count = len(inspect.getargspec(check_fn).args)
        if required_arg_count != 1:
            error = ("'check' must be a function of one argument, but"
                     " it is defined with {} required arguments (on line {})"
                     .format(required_arg_count, check_definition_linum))
            raise JFLAPTestFileParseError(error)
        for word, result in tests.items():
            # Only call "check" if the desired result has not been
            # manually specified.
            if result is None:
                try:
                    result = check_fn(word)
                except Exception as e:
                    error = ("error on line {} while invoking"
                             " check('{}'): {}: {}"
                             .format(check_definition_linum + (exception_linum() - 1),
                                     word,
                                     exception_name(e),
                                     e.message))
                    raise JFLAPTestFileParseError(error)
                tests[word] = bool(result)
    return tests


# API functions

def testFileParser(filename):
    """Parses the provided test file, returning a list of test names.

    See the user manual for more information about this API function."""
    with open(filename) as f:
        try:
            return parse_test_file_contents(f.read()).keys()
        except JFLAPTestFileParseError:
            traceback.print_exception(sys.last_traceback)
            return []


class CouldNotRunJFLAPTestsError(Exception):
    """Exception thrown when none of the JFLAP tests could be run, due to
    an error."""
    pass


def run_tests(command_prefix, test_file, time_limit):
    """Wrapper for "runTests" that adheres to PEP8 variable naming
    conventions."""
    try:
        with open(test_file) as f:
            try:
                tests = parse_test_file_contents(f.read())
            except JFLAPTestFileParseError as e:
                error = ("Could not parse test file '{}': {}"
                         .format(test_file, e.message))
                raise CouldNotRunJFLAPTestsError(error)
            # Determine the containing directory and literal filename
            # for the test file.
            directory, test_filename = os.path.split(test_file)
            if not directory:
                directory = "."
            # Find all the JFLAP files that the test_file might
            # possibly be testing.
            jflap_filenames = []
            for file in os.listdir(directory):
                if file.endswith(".jff"):
                    jflap_filenames.append(file)
            # If there's only one JFLAP file, nothing fancy is needed,
            # because there's only one choice.
            if len(jflap_filenames) == 1:
                jflap_filename = jflap_filenames[0]
            else:
                # Otherwise, we need to try to guess which file to
                # test by swapping out the extension of the test file
                # for ".jff".
                try:
                    extensionIndex = test_filename.rindex(".")
                except ValueError:
                    error = ("Test file '{}' does not have an extension"
                             .format(test_filename))
                    raise CouldNotRunJFLAPTestsError(error)
                jflap_filename = test_filename[:extensionIndex] + ".jff"
                if jflap_filename not in jflap_filenames:
                    # We could try harder to find a match, or allow
                    # specifying the filename of the corresponding
                    # JFLAP file within the test file, but to be
                    # honest that wouldn't really provide much help
                    # (because if you can put the name of the JFLAP
                    # file in the test file, you can just name the
                    # test file instead).
                    error = ("Test file '{}' does not match any of the"
                             " available JFLAP files, which are: {}"
                             .format(test_filename,
                                     ", ".join("'{}'".format(file)
                                               for file in jflap_filenames)))
                    raise CouldNotRunJFLAPTestsError(error)
            jflap_file = os.path.join(directory, jflap_filename)
            failedTests = {}
            all_stdout = ""
            all_stderr = ""
            # To ensure that this process does not take longer
            # than the provided time limit, we divide the time
            # equally among each test.
            if time_limit:
                timeout = time_limit / len(tests)
            else:
                timeout = None
            # We'll also need to figure out the directory containing
            # this Python file, so we can find jflaplib-cli.jar.
            script_directory = os.path.split(__file__)[0]
            for word, should_accept in tests.items():
                # See [1] for the source code of jflaplib-cli.jar.
                # Note that the command-line parsing library used by
                # jflaplib-cli, JCommander, has an odd quirk in the
                # way it parses arguments. First it trims whitespace
                # from both ends of each argument, and then it removes
                # a pair of double quotes if one exists. So, to ensure
                # an argument is interpreted literally, we just wrap
                # it in double quotes! See [2] for discussion of this
                # issue.
                #
                # [1]: https://github.com/raxod502/jflap-lib
                # [2]: https://github.com/cbeust/jcommander/issues/306
                command = Command(command_prefix +
                                  ["java",
                                   # The following system property
                                   # prevents the Java process from
                                   # showing up in the Mac app
                                   # switcher, which is extremely
                                   # annoying.
                                   "-Dapple.awt.UIElement=true",
                                   "-jar",
                                   os.path.join(script_directory,
                                                "jflaplib-cli.jar"),
                                   "run",
                                   jflap_file,
                                   '"{}"'.format(word)])
                timed_out, stdout, stderr = command.run(
                    timeout=timeout,
                    env=os.environ)
                all_stdout += stdout
                all_stderr += stderr
                if timed_out:
                    error = ("Timed out (took more than {} seconds)"
                             .format(timeout))
                    failedTests[word] = {"hint": error}
                else:
                    # jflaplib-cli should print "true" or "false",
                    # depending on whether the NFA or Turing
                    # machine accepted or rejected the input. But
                    # we handle all the possible edge cases here,
                    # just in case.
                    contains_true = "true" in stdout
                    contains_false = "false" in stdout
                    if contains_true and contains_false:
                        stdout = stdout.strip()
                        if not stdout:
                            stdout = "(none)"
                        stderr = stderr.strip()
                        if not stderr:
                            stderr = "(none)"
                        error = ("JFLAP reported both 'accept' and"
                                 " 'reject', output: {}; error: {}"
                                 .format(stdout.strip(), stderr.strip()))
                        failedTests[word] = {"hint": error}
                    elif not (contains_true or contains_false):
                        stdout = stdout.strip()
                        if not stdout:
                            stdout = "(none)"
                        stderr = stderr.strip()
                        if not stderr:
                            stderr = "(none)"
                        error = ("JFLAP reported neither 'accept' nor"
                                 " 'reject', output: {}; error: {}"
                                 .format(stdout.strip(), stderr.strip()))
                        failedTests[word] = {"hint": error}
                    elif contains_true is not should_accept:
                        error = ("This word should have been {}, but it"
                                 " was {}"
                                 .format(result_to_str(should_accept),
                                         result_to_str(contains_true)))
                        failedTests[word] = {"hint": error}
            summary = {"died": False,
                       "timeout": False,
                       "totalTests": len(tests),
                       "failedTests": len(failedTests),
                       "rawOut": all_stdout,
                       "rawErr": all_stderr}
            return summary, failedTests
    except Exception as e:
        if isinstance(e, CouldNotRunJFLAPTestsError):
            # If the error is a CouldNotRunJFLAPTestsError, then this
            # code generated the error message and included all
            # necessary information. So we can just return the
            # message.
            error = e.message
        else:
            # Otherwise, there was an unexpected error, and we'll
            # provide the whole stack trace for debugging purposes.
            # This is obviously very bad from a security perspective,
            # but worrying about it would be like making sure to turn
            # out the lights when the building is on fire, given the
            # security of the rest of this website.
            error = traceback.format_exc()
        summary = {"died": True,
                   "timeout": False,
                   "totalTests": 0,
                   "failedTests": 0,
                   "rawOut": "",
                   "rawErr": error}
        failedTests = {}
        return summary, failedTests


def runTests(cmdPrefix, testFile, timeLimit):
    """Runs the tests defined in testFile, returning a tuple of dictionaries.

    See the user manual for more information about this API function."""
    return run_tests(cmdPrefix, testFile, timeLimit)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        for filename in sys.argv[1:]:
            print(run_tests([], filename, None))
    else:
        doctest.testmod()
