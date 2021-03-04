#!/usr/bin/env python3

import json
import os
import subprocess as sp
import sys

assert sys.argv[1] in ('--points', '--comments')

points = sys.argv[1] == '--points'

results_dir = sys.argv[2]

POINTS_PER_TEST = 2
BASELINE_POINTS = 1

def copy_to_clipboard(contents):
    sp.call(['./copy.sh', contents])

for result_file in os.listdir(results_dir):
    if(not result_file.endswith('.json')):
        continue
    with open(os.path.join(results_dir, result_file)) as f:
        data = json.load(f)
    total_tests = len(data['summary']['testsAll'])
    passed_tests = len(data['summary']['testsPassed'])
    failed_tests = len(data['summary']['testsFailed'])
    score = passed_tests * POINTS_PER_TEST + BASELINE_POINTS
    if points:
        print(score)
    else:
        comment = []
        if failed_tests == 0:
            comment += ['You passed all the tests. Good job!']
        else:
            comment += ['You failed ' + str(failed_tests) + ' test' +
                        ('s' if failed_tests != 1 else '') +
                        ' out of ' + str(total_tests) + '.']
        for case, info in data['tests'].items():
            if info['passed'] is False:
                if info['terminated'] is False:
                    reason = 'simulation did not terminate'
                elif info['valid'] is False:
                    reason = 'simulation produced an error'
                elif info['correct'] is False:
                    reason = 'wrong answer'
                else:
                    reason = 'not sure what went wrong'
                comment += ['- ' + case + ': ' + reason]
        comment = '\n'.join(comment)
        print('For result file: ' + result_file)
        print('-' * 80)
        print(comment)
        print('-' * 80)
