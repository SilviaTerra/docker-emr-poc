import json
import os
from subprocess import Popen, PIPE
from sys import platform as _platform
import uuid


TIMEOUT = '5m'  # 5 minutes
DOCKER_IMAGE = 'silviaterra/emr-poc'

if _platform == "linux" or _platform == "linux2":
    TIMEOUT_FUNC = 'timeout'
    DOCKER = 'sudo docker'  # TODO remove after figuring out EMR group issue
elif _platform == 'darwin':
    TIMEOUT_FUNC = 'gtimeout'
    DOCKER = 'docker'
else:
    raise Exception('Unsupported platform "%s"' % _platform)

SHARED_DIR = os.path.expanduser('~/docker-mnt')

# Commands for pulling and updating docker image.  Only used in bootstrap
# script so have forced sudo for now
# TODO remove sudo in these 3 commands after
# figuring out "docker" group issue on EMR
PULL_CMD = 'sudo docker pull %s' % DOCKER_IMAGE
UPDATE_CMD = ' '.join([
    'sudo docker run -d',
    DOCKER_IMAGE,
    '/bin/bash -c',
    '"cd /opt/docker-emr-poc; git pull; cd -; sleep 2m"'
    # NOTE - the 2m sleep is so the container hangs around long enough
    # for us to run the "docker commit" command
])
COMMIT_CMD = 'sudo docker commit `sudo docker ps -ql` %s' % DOCKER_IMAGE


def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen('%s %s %s' % (DOCKER, action, ctr_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def execute(cmd):
    """
    From http://blog.bordage.pro/avoid-docker-py/

    cmd is a list.  Should contain the command + args in a list, e.g.
    ['sh','my_script.sh']
    """

    container_name = str(uuid.uuid4())

    docker_prefix = [TIMEOUT_FUNC, '-s', 'SIGKILL', TIMEOUT] \
        + DOCKER.split(' ') \
        + ['run', '-v', '%s:/mnt/vol' % SHARED_DIR,
            '--rm', '--name', container_name, DOCKER_IMAGE]

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
