#!/usr/bin/python

import json
import sys


def manipulator(input_string):
    """
    Do a thing to input
    """

    print 'Simulate random garbage print statements'

    if input_string == 'Nasty hobbitses':
        raise Exception('YOLO')

    return {
        'status': 'OK',
        'message': 'Howdy there %s' % input_string,
        'a number': 5
    }


if __name__ == "__main__":
    # get input
    in_string = sys.argv[1]

    # manipulate input
    output = manipulator(in_string)

    # write output in json in stdout
    print json.dumps(output)
