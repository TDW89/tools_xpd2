#! /usr/bin/env python

from github import Github
import pexpect
import logging
import os
import platform
import re
import subprocess
import sys
import tempfile
import time

ostype = platform.system()

if not re.match('.*Darwin.*', ostype) and re.match('.*[W|w]in.*', ostype):
    concat_args = True
    use_shell = True
else:
    concat_args = False
    use_shell = False

def Popen(*args, **kwargs):    
    kwargs['shell'] = use_shell
#    kwargs['bufsize'] = 1
    if concat_args:
        args = (' '.join(args[0]),) + args[1:]
    try:
        return subprocess.Popen(*args, **kwargs)
    except:
        sys.stderr.write("ERROR: Cannot run command `%s'\n"%' '.join(args[0]))
        sys.stderr.write("ABORTING\n")
        sys.exit(1)

def call(command, cwd=None):
    """ Run the command requested and return the stdout/stderr expected
    """
    logging.debug("Run: %s" % ' '.join(command))

    # Create temporary files to pass stdout and stderr to since on Windows the
    # less/more-like behaviour waits for a keypress if it goes to stdout.
    out = tempfile.TemporaryFile()
    err = tempfile.TemporaryFile()
    process = Popen(command, cwd=cwd, stdout=out, stderr=err)
    out.seek(0)
    err.seek(0)

    stdout_lines = [line.strip() for line in out.readlines()]
    catch_errors(stdout_lines)
    stderr_lines = [line.strip() for line in err.readlines()]
    catch_errors(stderr_lines)
    if stdout_lines or stderr_lines:
        logging.debug('\n'.join(stderr_lines))
        logging.debug('\n'.join(stdout_lines))
    return (stdout_lines, stderr_lines)


class Expect(object):
    """ Container for an expected output and its response.
        The default timeout version is the default for pexpect.
    """
    def __init__(self, value=None, send=None, timeout=-1):
        self.value = value
        self.send = send
        self.timeout = timeout


def interact(command, expected, cwd=None):
    """ Interact with a process given a list of expected output and responses.
        Also keeps track of all output seen to check for errors at the end
    """
    if cwd:
        os.chdir(cwd)
    logging.debug("Interact: %s" % ' '.join(command))
    process = pexpect.spawn(' '.join(command), timeout=10)

    all_output = ''
    for expect in expected:
        if expect.value:
            logging.debug("interact: expect '%s'" % expect.value)
            try:
                process.expect(expect.value, timeout=expect.timeout)
                if process.before:
                    all_output += process.before
                if process.after:
                    all_output += process.after
            except pexpect.EOF:
                logging.error("interact: unexpected EOF")
                process.close()
                return
            except pexpect.TIMEOUT:
                logging.error("interact: TIMEDOUT")
                process.close()
                return
                
        # Want to be able to send blank lines (use default value) hence not None check
        if expect.send is not None:
            logging.debug("interact: send '%s'" % expect.send)
            process.sendline(expect.send)

    process.expect(pexpect.EOF)
    if process.before:
        all_output += process.before

    # Required according to pexpect documentation to guarantee process has been updated
    time.sleep(0.1)
    assert not process.isalive()

    catch_errors(all_output)

def catch_errors(lines):
    for line in lines:
        if re.search('^Traceback', line):
            logging.error('Backtrace produced')

def check_exists(test, files):
    for f in files:
        if not os.path.exists(f):
            logging.error("%s: missing %s" % (test, f))

def get_apps_from_github(tests_folder):
    """ Clone all the public repos from github. If the folder already exists then simply
        update it.
    """
    github = Github()
    org = github.get_organization("Xcore")
    repos = org.get_repos("public")
    for repo in repos:
        os.chdir(tests_folder)

        test_name = "test_" + repo.name
        test_folder = os.path.join(test_name, repo.name)

        if os.path.exists(test_folder):
            logging.info("Updating %s" % repo.name)
            os.chdir(test_folder)
            os.system('git pull')

        else:
            logging.info("Cloning %s" % repo.name)
            if not os.path.exists(test_name):
                os.mkdir(test_name)
            os.chdir(test_name)
            os.system('git clone ' + repo.clone_url)


