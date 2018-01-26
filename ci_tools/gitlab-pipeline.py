#!/usr/bin/env python3
#
# Tool to interact with Gitlab inside pipelines.
#
# Copyright (c) 2018, Andrea Cervesato <andrea.cervesato@mailbox.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# pylint: disable=invalid-name

import os
import sys
import argparse
import urllib.parse
import urllib.request

args_parser = None

class GitlabPipeline(object):
    """
    A simple class to interact inside Gitlab pipeline.
    """
    def __init__(self):
        # the CI_TESTER_TOKEN is created by Gitlab's admin
        # (Settings -> CI/CD -> Secret Variables) and it contains
        # the token that has to be used by this script in order to
        # setup the 'PRIVATE-TOKEN' HTTP header variable
        self._ci_private_token = os.environ['CI_TESTER_TOKEN']
        self._ci_project_url = os.environ['CI_PROJECT_URL']
        self._ci_commit_reg_name = os.environ['CI_COMMIT_REF_NAME']
        self._ci_project_id = os.environ['CI_PROJECT_ID']

    def delete_current_branch(self):
        """
        Delete the current Gitlab branch.
        """
        # extract the hostname from CI_PROJECT_URL variable
        url = urllib.parse.urlparse(self._ci_project_url)

        # remove '/' char from the branch name
        branch = self._ci_commit_reg_name.replace('/', '%2F')

        # create the complete url request
        url = "http://%s/api/v4/projects/%s/repository/branches/%s" % (
            url.netloc, self._ci_project_id, branch
        )

        # send the delete request
        sys.stdout.write("sending HTTP 'DELETE' request to %s\n" % url)

        request = urllib.request.Request(url=url, method='DELETE')
        request.add_header("PRIVATE-TOKEN", self._ci_private_token)
        return urllib.request.urlopen(request)

def _main(args):
    # check if args are given
    if len(vars(args)) == 0:
        args_parser.print_help()
        exit(1)

    # create the Gitlab pipeline communicator
    gl_pipeline = GitlabPipeline()

    # start any operation on Gitlab
    if args.delete_current_branch:
        response = gl_pipeline.delete_current_branch()
        sys.stdout.write(str(response.read()))
        exit(0)

if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(\
        description="Tool to interact into Gitlab pipelines")
    args_parser.add_argument('-d', '--delete-current-branch', \
        action='store_true', \
        help="delete the current branch")

    _main(args_parser.parse_args())
