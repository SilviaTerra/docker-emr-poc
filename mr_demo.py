from mrjob.job import MRJob
from mrjob.step import MRStep

from utils import docker

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


if __name__ == '__main__':
    MRDemo.run()
