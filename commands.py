# -*- coding:utf-8 -*-

from flask.ext.script import Command, Option
from flask import url_for

import os
import config


class Test(Command):
    """Run tests."""

    start_discovery_dir = "tests"

    def get_options(self):
        return [
            Option('--start_discover', '-s', dest='start_discovery',
                   help='Pattern to search for features',
                   default=self.start_discovery_dir),
        ]

    def run(self, start_discovery):
        import unittest

        if os.path.exists(start_discovery):
            argv = [config.project_name, "discover"]
            argv += ["-s", start_discovery]

            unittest.main(argv=argv)
        else:
            print("Directory '%s' was not found in project root." % start_discovery)

class ListRoutes(Command):
    """List Routes """

    def run(self):
        import urllib
        from main import app_factory
        app = app_factory(config.Dev)

        output = []
        for rule in app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)


            methods = ','.join(rule.methods)
            try:
                url = url_for(rule.endpoint, **options)
                line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            except:
                line = "{:50s} {:20s} {}".format(rule.endpoint, methods, rule.rule)
            output.append(line)

        for line in sorted(output):
            print line