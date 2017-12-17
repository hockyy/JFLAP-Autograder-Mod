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

    $ ./grade.py
        [--timeout <timeout>]
        <input-jff-or-directory> <output-file-or-directory>


If you provide a file, then that file is graded. If you provide a
directory, then all of the files in that directory are graded.

If the input was a file, the output is also a file. Otherwise, the
output goes into a directory, which is created if absent, and the
filenames are generated automatically based on the input files by
appending `.json`.

The timeout is in seconds. If not provided, none is used.

Next, you can convert the grading output into whatever format you'd
like. An example script for doing this is provided
(`format_for_canvas.py`). To understand the output format, please
refer to the following example:

    {
      "tests": {
        "01100": {
          "expected": true,
          "actual": false,
          "terminated": true,
          "valid": true,
          "correct": false,
          "passed": false,
          "output": {
            "stdout": "...",
            "stderr": "..."
          }
        },
        "110": {
          "expected": false,
          "actual": false,
          "terminated": true,
          "valid": true,
          "correct": true,
          "passed": true,
          "output": {
            "stdout": "...",
            "stderr": "..."
          }
        },
        "": {
          "expected": true,
          "actual": null,
          "terminated": false,
          "valid": null,
          "correct": null,
          "passed": false,
          "output": {
            "stdout": "...",
            "stderr": "..."
          }
        },
        "foobar": {
          "expected": false,
          "actual": null,
          "terminated": true,
          "valid": false,
          "correct": null,
          "passed": false,
          "output": {
            "stdout": "...",
            "stderr": "..."
          }
        }
      },
      "summary": {
        "testsAll": ["01100", "110", "", "foobar"],
        "testsTerminated": ["01100", "110", "foobar"],
        "testsDidNotTerminate": [""],
        "testsValid": ["01100", "110"],
        "testsInvalid": ["foobar"],
        "testsCorrect": ["110"],
        "testsIncorrect": ["01100"],
        "testsPassed": ["110"],
        "testsFailed": ["01100", "", "foobar"]
      },
      "info": {
        "filename": ".../submission.jff",
        "timeout": 5,
        "timestamp": "2017-12-17T08:39:25.466647"
      }
    }

[jflapgrader]: jflapgrader.py
