import json
import os
import shutil
import subprocess
import operator
import click
import requests
from lxml import html
from email_util import send_email, build_content

requests.packages.urllib3.disable_warnings()


class Config(object):

    def __init__(self):
        self.repo_path = "/tmp/test_repo/"


pass_config = click.make_pass_decorator(Config, ensure=True)


def echo_success(msg):
    click.echo(click.style(msg, fg='green'))


def echo_error(msg):
    click.echo(click.style(msg, fg='red'))


def echo_skip(msg):
    click.echo(click.style(msg, fg='cyan'))


def git_clone(remote_path, local_path):
    cmd = ["/bin/git clone {0} {1}".format(remote_path, local_path)]
    subprocess.check_output(cmd, shell=True)


def git_pull(local_path):
    cmd = ["cd {0} && /bin/git pull {0}".format(local_path)]
    subprocess.check_output(cmd, shell=True)


def get_directory(file_path):
    return "/".join(file_path.split("/")[:-1])


def get_all_failed_tests():
    with open('/tmp/failed_tests.txt', 'r') as filehandle:
        failed_tests = json.load(filehandle)
        return failed_tests


def get_author_details(author_file):
    with open(author_file, 'r') as filehandle:
        failed_tests = json.load(filehandle)
        return failed_tests


def check_test_path(test_name, test_path, filter):
    if filter is not None:
        cmd = ["/bin/grep -rl {0} {1} | grep {2}".format(test_name, test_path, filter)]
    else:
        cmd = ["/bin/grep -rl {0} {1} ".format(test_name, test_path)]
    test_path = (subprocess.check_output
                 (cmd, shell=True, stderr=subprocess.STDOUT)).decode('utf-8').rstrip()
    if len(test_path.split('\n')) > 1:
        return test_path.split('\n')
    return test_path


def get_git_blame_output(test_name, test_path):
    cmd = ["/bin/grep -m 1 -irnh '{0}' {1} | cut -f1 -d:".format(test_name, test_path)]
    line_number = (subprocess.check_output
                   (cmd, shell=True, stderr=subprocess.STDOUT)).decode('utf-8').rstrip()
    cmd = ["cd {0} && /bin/git blame --line-porcelain -L {1},{1} {2} | grep 'author-mail'".format
           (get_directory(test_path), line_number, test_path)]
    return (subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT))\
        .decode('utf-8').rstrip()


def remove_duplicate_test(test_path, test):
    counter_list = {}
    for path in test_path:
        counter = 0
        for string in test.split('.'):
            if string in path:
                counter = counter+1
        counter_list[path] = counter
    return max(counter_list.items(), key=operator.itemgetter(1))[0]


def collect_failed_tests(url):
    if bool(url.strip()):
        try:
            page = requests.get(url, verify=False,)
            tree = html.fromstring(page.content)
            failed_tests = tree.xpath('//a[contains(@onclick, "hideFailureSummary")]/following-sibling::a/text()')
            return failed_tests
        except Exception as err:
            return err
    else:
        raise Exception(echo_error("Something wrong with jenkins url/host"))


def get_test_blame(test, test_name, test_path, email, filter=""):
    try:
        if not test_path.endswith('.py'):
            test_path = check_test_path(test_name=test_name, test_path=test_path, filter=filter)
        if isinstance(test_path, list):
            test_path = remove_duplicate_test(test_path, test)
        git_blame_output = get_git_blame_output(test_path=test_path, test_name=test_name)
        if email is not None and email in git_blame_output:
            return "{0} => Failed ".format(test)
        else:
            return None
    except subprocess.CalledProcessError:
        return "{0} => Skipped ".format(test)


def get_test_blame_with_author(test, test_name, test_path, email, filter=""):
    try:

        if not test_path.endswith('.py'):
            test_path = check_test_path(test_name=test_name, test_path=test_path, filter=filter)
        if isinstance(test_path, list):
            test_path = remove_duplicate_test(test_path, test)
        git_blame_output = get_git_blame_output(test_path=test_path, test_name=test_name)

        git_blame = (git_blame_output, test)
        return git_blame
    except subprocess.CalledProcessError:
        return "{0} => Skipped ".format(test)


@click.group()
def cli():
    """This CLI tool to gather failed tests based on commit history
       """
    pass


@cli.command()
@click.option('--git-url', default="",
              help="Pass the git url for test repo ")
@click.option('--jenkins-url', default="",
              help="Pass the jenkins url to collect the failed tests")
@click.option('--clone-path', default="/tmp/test_repo/",
              help="Pass the path to clone repos to",)
@pass_config
def set_config(config, git_url, jenkins_url, clone_path):
    """Set git_url and jenkins_url to collect the
    failed tests"""
    config.repo_path = clone_path
    if os.path.exists(config.repo_path):
        shutil.rmtree(config.repo_path)
    try:
        if None not in (git_url, jenkins_url):
            git_clone(git_url, config.repo_path)
            failed_tests = collect_failed_tests(jenkins_url)
            with open('/tmp/failed_tests.txt', 'w') as filehandle:
                json.dump(failed_tests, filehandle)
            echo_success("Configs are set correctly !")
        else:
            echo_error("Something went wrong !")
    except Exception as err:
        click.echo(err)


@cli.command()
@click.option('--jenkins-url', default=None,
              help="Pass the jenkins url to collect the failed tests")
@click.option('--clone-path', default="/tmp/test_repo/",
              help="Pass the path to clone repos to",)
@pass_config
def refresh_config(config, jenkins_url, clone_path):
    """Update config, pass new jenkins test-result url and clone-path"""
    config.repo_path = clone_path
    if jenkins_url is not None:
        if config.repo_path is not None:
            git_pull(config.repo_path)
        failed_tests = collect_failed_tests(jenkins_url)
        with open('/tmp/failed_tests.txt', 'w') as filehandle:
            json.dump(failed_tests, filehandle)
        echo_success("Configs are refreshed successfully !")
    else:
        echo_error("Something went wrong !")


@cli.command()
@click.option('--local-repo', default=None,
              help="Provide test local repo if required")
@click.option('--filter', default=None,
              help="Pass filter if local-repo is enabled")
@click.option('--email', default=None,
              help="Pass email to get tests based on git commit history")
@click.option('--skip', default=" ",
              help="Pass search string to skip the specific tests")
@pass_config
def show_my_tests(config, local_repo, filter, email, skip):
    """Pass github email to see failed tests"""
    failed_tests = get_all_failed_tests()
    tests = []
    with click.progressbar(failed_tests, label='Searching failed tests') as bar:
        for test in bar:
            if skip not in test and email is not None and str(filter) not in test:
                test_name = str(test).split('.')[-1]
                if local_repo is None:
                    repo_path = config.repo_path + "/".join(test.split('.')[:1])
                    test_name = get_test_blame(test, test_name, repo_path, email, filter)
                elif local_repo is not None:
                    test_name = get_test_blame(test, test_name, local_repo, email, filter)
                if test_name is not None:
                    tests.append(test_name)
            elif skip not in test and filter in test:
                tests.append("{0} => Failed ".format(test))
    if not len(tests) == 0:
        for mark_test in tests:
            if '=> Skipped' in mark_test:
                echo_skip(mark_test)
            else:
                echo_error(mark_test)
    else:
        echo_success("No Tests Found!")


@cli.command()
@click.option('--local-repo', default=None,
              help="Provide test local repo if required")
@click.option('--email', default="",
              help="Provide Email Report for Specific")
@click.option('--skip', default=" ",
              help="Pass search string to skip the specific tests")
@click.option('--filter', default=None,
              help="Pass filter if local-repo is enabled")
@click.option('--from_email', default=" ",
              help="Pass from email address")
@click.option('--to_email', default=" ",
              help="Pass to email address")
@click.option('--subject', default=" ",
              help="Pass subject")
@click.option('--component', default=None,
              help="pass json file path containing author and component tags")
@pass_config
def send_email_report(config, local_repo, email, skip, filter,
                      from_email, to_email, subject, component):
    """Send an email report based on git commit history"""
    failed_tests = get_all_failed_tests()
    author_tests = {}
    git_blame = ()
    if component is None:
        with click.progressbar(failed_tests, label='Searching failed tests') as bar:
            for test in bar:
                if skip not in test and email is not None and str(filter) not in test:
                    test_name = str(test).split('.')[-1]
                    if local_repo is None:
                        repo_path = config.repo_path + "/".join(test.split('.')[:2])
                        git_blame = get_test_blame_with_author(test, test_name, repo_path, email, filter)
                    elif local_repo is not None:
                       git_blame = get_test_blame_with_author(test, test_name, local_repo, email, filter)
                    if git_blame[0] not in author_tests:
                        author_tests[git_blame[0]] = [git_blame[1]]
                    else:
                        author_tests[git_blame[0]].append(git_blame[1])
    else:
        with click.progressbar(failed_tests, label='Searching failed tests') as bar:
            for test in bar:
                if skip not in test and str(filter) not in test:
                    test_name = str(test).split('.')[-1]
                    repo_path = config.repo_path + "/".join(test.split('.')[:2])
                    test_path = check_test_path(test_name=test_name, test_path=repo_path, filter=None)
                    if isinstance(test_path, list):
                        test_path = remove_duplicate_test(test_path, test)
                    author_details = get_author_details(component)
                    for author, tags in author_details.items():
                        for tag in tags:
                            if tag.lower() in test_path.lower():
                                if author not in author_tests:
                                    author_tests[author] = [test]
                                else:
                                    author_tests[author].append(test)
                                break
    content = build_content(author_tests)
    for author, tests in author_tests.items():
        echo_error("==" * 55)
        echo_error("{: ^50s}".format(author))
        echo_error("==" * 55)
        echo_error("\n".join(tests))
    send_email(from_email=from_email, to_email=to_email,
               content=content, subject=subject)
    if not len(author_tests) == 0:
        echo_success("Email Report Sent Successfully! ")
    else:
        echo_success("No Tests Found!")


@cli.command()
@pass_config
def show_all_tests(config):
    """Show all failed test names"""
    failed_tests = get_all_failed_tests()
    for test in failed_tests:
        echo_error(test)