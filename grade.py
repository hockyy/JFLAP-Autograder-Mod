#!/usr/bin/env python

import jflapgrader
import os

test_file = 'tests'
for jflap_filename in os.listdir('submissions'):
    jflap_file = os.path.join('submissions', jflap_filename)
    results_file = os.path.join('results', jflap_filename + '.out')
    print 'Testing ' + jflap_file
    results = jflapgrader.run_tests(jflap_file, test_file, time_limit=60)
    with open(results_file, 'w') as f:
        f.write(repr(results))
    print results
