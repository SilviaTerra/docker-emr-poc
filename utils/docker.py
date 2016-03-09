import json
from subprocess import Popen, PIPE
from sys import platform as _platform
import uuid


TIMEOUT = '5m'  # 5 minutes
DOCKER_IMAGE = 'silviaterra/emr-poc'


def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen('docker %s %s' % (action, ctr_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def execute(cmd):
    """
    From http://blog.bordage.pro/avoid-docker-py/

    cmd is a list.  Should contain the command + args in a list, e.g.
    ['sh','my_script.sh']
    """
    if _platform == "linux" or _platform == "linux2":
        TIMEOUT_FUNC = 'timeout'
    elif _platform == 'darwin':
        TIMEOUT_FUNC = 'gtimeout'
    else:
        raise Exception('Unsupported platform "%s"' % _platform)

    container_name = str(uuid.uuid4())

    docker_prefix = [
        TIMEOUT_FUNC, '-s', 'SIGKILL', TIMEOUT,
        'docker', 'run', '--rm', '--name', container_name, DOCKER_IMAGE
    ]
    docker_prefix = []  # TODO remove

    p = Popen(docker_prefix + cmd, stdout=PIPE, stderr=PIPE)

    if p.wait() == -9:  # Happens on timeout
        # We have to kill the container since it still runs
        # detached from Popen and we need to remove it after because
        # --rm is not working on killed containers
        kill_and_remove(container_name)
        raise Exception('Timeout running command "%s"' % ' '.join(cmd))
    elif p.wait() != 0:
        raise Exception(p.stderr.read())
    else:
        return p.stdout.readlines()


def run_my_cmd(cmd):
    """
    Run a command in Docker and return output.
    Note, this expects that the command being executed prints its output
    as JSON on the last line of stdout before it returns.
    """
    output_lines = execute(cmd)
    return json.loads(output_lines[-1])  # get last line for JSON output
