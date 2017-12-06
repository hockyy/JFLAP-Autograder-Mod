#!/usr/bin/env python3

import os
import subprocess as sp
import sys

assert sys.argv[1] in ('--points', '--comments')

points = sys.argv[1] == '--points'

POINTS_PER_TEST = 2
BASELINE_POINTS = 1

for result_file in os.listdir('results'):
    if result_file == '.gitkeep':
        continue
    with open(os.path.join('results', result_file)) as f:
        text = f.read()
        # Hey, it's the easiest way :D
        result = eval(text)
    total_tests = result[0]['totalTests']
    failed_tests = result[0]['failedTests']
    passed_tests = total_tests - failed_tests
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
        for case, extra in result[1].items():
            hint = extra['hint']
            comment += ['- ' + case + ': ' + hint]
        comment = '\n'.join(comment)
        print('For result file: ' + result_file)
        print('-' * 80)
        print(comment)
        print('-' * 80)
        sp.call(['./copy.sh', comment])
        input()
