#!/usr/bin/env python3

import jflapgrader
import json
import os
import sys

NAME = sys.argv[0]

USAGE = """\
usage: {}
         [--timeout <timeout>]
         <input-jff-or-directory> <output-file-or-directory> <test-file>\
""".format(NAME)

def print_stderr(msg, *args, **kwargs):
    print(msg, *args, **kwargs, file=sys.stderr)

def error_and_exit(msg, *args, **kwargs):
    print_stderr('{}: {}'.format(NAME, msg), *args, **kwargs)
    sys.exit(1)

def usage_and_exit(*args, **kwargs):
    print_stderr(USAGE, *args, **kwargs)
    sys.exit(1)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) not in (3, 5):
        usage_and_exit()
    if len(args) == 5:
        if args[0] != "--timeout":
            usage_and_exit()
        try:
            timeout = float(args[1])
        except ValueError:
            error_and_exit(
                "timeout '{}' is not a number".format(args[1]))
    else:
        timeout = None
    input_path, output_path, test_file = args[-3:]

    # Take care of the test file check first, since it's the easiest.
    if not os.path.isfile(test_file):
        error_and_exit("no such file: " + test_file)

    # Make sure the input is an existing file or directory.
    if not os.path.exists(input_path):
        error_and_exit("no such file or directory: " + input_path)

    # We will be producing multiple output files if the input is a
    # directory.
    mapping = os.path.isdir(input_path)

    # The input list is either a single file, or the contents of the
    # input directory.
    if mapping:
        # If we are producing multiple output files, the output must
        # be a directory. Make sure it exists.
        try:
            if not os.path.isdir(output_path):
                os.mkdir(output_path)
        except OSError:
            error_and_exit("could not create directory: " + output_path)

        # Determine the input filenames.
        try:
            fnames = os.listdir(input_path)
        except FileNotFoundError:
            error_and_exit("could not list directory: " + input_path)

        # Compute the input and output lists.
        inputs = [os.path.join(input_path, fname) for fname in fnames]
        outputs = [os.path.join(output_path, fname) for fname in fnames]
    else:
        # There is only one input filename.
        inputs = [input_path]

        # We will produce a single file either at the specified path
        # or inside the directory named.
        if os.path.isdir(output_path):
            outputs = [os.path.join(output_path, os.path.split(input_path)[0])]
        else:
            parent_dir = os.path.split(output_path)[0]
            if not os.path.isdir(parent_dir):
                error_and_exit("directory does not exist: " + parent_dir)
            outputs = [output_path]

    # Now do the actual mapping.
    for input_name, output_name in zip(inputs, outputs):
        if os.path.exists(output_name):
            print("already exists, skipping: '{}'".format(output_name))
        else:
            print("generating: '{}'".format(output_name))
            data = jflapgrader.run_tests(input_name, test_file, timeout)
            with open(output_name) as f:
                json.dump(data, f)
