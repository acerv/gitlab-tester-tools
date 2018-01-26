# Table of contents
- [What is gitlab-tester-tools](#what-is-gitlab-tester-tools)
- [Gitlab setup](#gitlab-setup)
    - [Create tester user](#create-tester-user)
    - [Add tester user to your project](#add-tester-user-to-your-project)
    - [Setup testing secret token](#setup-testing-secret-token)
    - [Setting up the .gitlab-ci.yml file](#setting-up-the-gitlab-ciyml-file)
        - [Delete a branch from pipeline](#delete-a-branch-from-pipeline)
- [git-test plugin](#git-test-plugin)
    - [How to use the plugin](#how-to-use-the-plugin)
    - [How the plugin works](#how-the-plugin-works)
- [TODO](#todo)

# What is gitlab-tester-tools
Gitlab tester tools are a set of tools used to interact with Gitlab and
automatize the testing process during local development.

    $ git add <files i want to test>
    $ git test origin

Simple as that...Gitlab tester tools makes testers' lifes easier.

# Gitlab setup

## Create tester user
To create the `tester` user, go in the Admin Area, select `New user` and set
`Access Level` to `Regular`.
Once the creation process is finished, click on the `tester` user, in the Admin
Area and go to `Impersonation Tokens`, then set `Scopes` to `api`.

## Add tester user to your project
Go to the project page and under `Settings -> Members` add `tester` user
with Master role.

## Setup testing secret token
The token that is generated for `tester` user now can be used to send requests
to the Gitlab API. This can be done by exposing it to the pipeline environment
variables: go to `Settings -> CI / CD -> Secret variables` and create the
`CI_TESTER_TOKEN` variable with the token value of the `tester` user.

At this point, `tester` user is the access to our Gitlab API and its token is
exposed by `CI_TESTER_TOKEN`. All the times the project's pipeline will run,
`CI_TESTER_TOKEN` will be exposed in order to interact with Gitlab using the
HTTP protocol.

## Setting up the .gitlab-ci.yml file
The pipeline file `.gitlab-ci.yml`, in order to work with the ci tools has to
be configured properly.

### Delete testing branch from pipeline
An example on how to remove a branch from pipeline is the following:

    stages:
        - tests
        - cleanup

    mytests:
        stage: tests
        script:
            - echo "hello world"
        only:
            refs:
                - /^testing\/.*/

    delete-testing-branch:
        stage: cleanup
        script:
            - ci_tools/gitlab-pipeline.py -d
        # the cleanup must be executed on testing "temporary" branches only
        only:
            refs:
                - /^testing\/.*/
        # always run this stage even if the previous stages are failing
        when: always

In this example, the `delete-testing-branch` is always executed after any job
which fails or not. Its purpose is to remove the current branch with `testing/`
prefix.

With this setup, any branch starting with `testing/` prefix can be considered
as a "temporary branch" used to trigger `tests` stage.

# git-test plugin

## How to use the plugin
Git recognize plugins starting with `git-` prefix and inside the PATH, so, to
use the git-test plugin, PATH has to be initialized as following:

    export PATH=$PATH:<my parent path>/ci_tools

## How the plugin works
Note that to use this plugin the CI system must be configured to run tests
when a commit has been received inside a branch with `testing/` name suffix.
A way to do so in gitlab is to setup `.gitlab-ci.yml` like following:

    stages:
        - test

    tests:
        stage: test
        script:
            - echo "this is a test"
        only:
            refs:
                - /^testing\/.*/
                - master

When user runs `git test origin`, the plugin will upload the current
modifications inside a branch named `testing/<username>/<random string>`
in the `origin` server.

In particular, git-test plugin simplifies the following procedure:

    $ git stash --keep-index
    $ git push stash:refs/heads/testing/<username>/<random string>
    $ git stash pop

And it can be used in the following way:

    $ git add <my testing files>
    $ git test origin

# License
All the source code and documentation is released under the BSD license.