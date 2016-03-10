import os
import tarfile
from tempfile import NamedTemporaryFile

from mrjob.job import MRJob
from mrjob.step import MRStep

from utils import docker

EC2_KEY_PAIR = 'ec2-keypair'
EC2_KEY_PAIR_FILE = os.path.expanduser('~/.ssh/%s.pem' % EC2_KEY_PAIR)

CONTAINER_CMD = '/opt/docker-emr-poc/demo.py'


class MRDemo(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer)
        ]

    def mapper(self, _, value):
        for i in range(5):
            cmd_input = '%s-%s' % (value, i)
            output = docker.run_my_cmd(['python', CONTAINER_CMD, cmd_input])
            yield value, output

    def reducer(self, key, values):
        for v in values:
            yield key, v['message']

    def emr_job_runner_kwargs(self):
        kwargs = super(MRDemo, self).emr_job_runner_kwargs()

        kwargs['enable_emr_debugging'] = True
        kwargs['pool_emr_job_flows'] = True
        kwargs['max_hours_idle'] = 2
        kwargs['visible_to_all_users'] = True

        kwargs['ec2_key_pair'] = EC2_KEY_PAIR
        kwargs['ec2_key_pair_file'] = EC2_KEY_PAIR_FILE

        kwargs['ami_version'] = '3.10.0'

        kwargs['bootstrap'] = [
            # install docker
            'sudo yum update -y',
            'sudo yum install -y docker',
            'sudo service docker start',

            # add user to the "docker" group for access to daemon
            # TODO - this doesn't seem to work... the newgrp command
            #   drops us into a new shell and screws up execution
            # 'sudo usermod -a -G docker hadoop && newgrp docker',

            # pull docker images and update internal git repos
            docker.PULL_CMD,
            docker.UPDATE_CMD,
            'sleep 30s',  # give git repos time to pull
            docker.COMMIT_CMD
        ]

        # handle mr_demo dependencies
        filename = NamedTemporaryFile(suffix='.tar.gz').name
        directory = os.path.dirname(os.path.abspath(__file__))
        dependencies = ['__init__.py', 'utils/__init__.py', 'utils/docker.py']
        with tarfile.open(filename, 'w:gz') as tar:
            for arcname in dependencies:
                name = os.path.join(directory, arcname)
                tar.add(name, arcname)
        kwargs['setup'] = ['export PYTHONPATH=$PYTHONPATH:%s#/' % filename]

        return kwargs


if __name__ == '__main__':
    MRDemo.run()
