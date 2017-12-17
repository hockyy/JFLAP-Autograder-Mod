**JFLAP Autograder**: hopefully faster than running JFLAP tests by
hand.

## Building

* Make sure you cloned this repository recursively, i.e.

        $ git clone --recursive https://github.com/raxod502/JFLAP-Autograder.git

  If you didn't, you can fix it:

        $ git submodule update --init

* Install Maven. On macOS, this is:

        $ brew install maven

* Build `jflap-lib`:

        $ cd jflap-lib
        $ mvn package

## Usage

You will need:

* One or more student submission files (`.jff`) to grade.
* A test file to use. This is a plain text file, which has a pretty
  flexible format. See the docstring of `parse_test_file_contents`
  in [`jflapgrader.py`][jflapgrader] for detailed documentation of
  this format.

Then you can grade your submission(s) like so:

    $ ./grade.py <input-jff-or-directory> <output-file-or-directory>

If you provide a file, then that file is graded. If you provide a
directory, then all of the files in that directory are graded.

If the input was a file, the output is also a file. Otherwise, the
output goes into a directory, which is created if absent, and the
filenames are generated automatically based on the input files.

Next, you can convert the grading output into whatever format you'd
like. An example script for doing this is provided
(`format_for_canvas.py`).

[jflapgrader]: jflapgrader.py
