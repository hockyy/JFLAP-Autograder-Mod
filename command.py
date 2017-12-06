#! /usr/bin/env python
import threading
import subprocess
import traceback
import shlex


class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933

    Minor adaptations for use in the CS> system from kirpit's solution:
    https://gist.github.com/kirpit/1306188
    """
    command = None
    process = None
    returncode = None
    output, error = '', ''

    def __init__(self, command):
        if isinstance(command, basestring):
            command = shlex.split(command)
        self.command = command

    def run(self, timeout=None, compatibility=True, **kwargs):
        """Run a command.

        If compatibility mode is on (default), then return (timeout,
        output, error). Else return (returncode, output, error,
        timeout).
        """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.returncode = self.process.returncode
            except:
                self.error = traceback.format_exc()
                self.returncode = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE
        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        timeout = False
        if thread.is_alive():
            timeout = True
            if self.process:
                self.process.terminate()
                thread.join()
        if compatibility:
            return timeout, self.output, self.error
        else:
            return self.returncode, self.output, self.error, timeout
