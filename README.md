# testblame
This CLI tool to gather failed tests based on git commit history and sends emails  


[Features](https://github.com/omkarkhatavkar/testblame#1-features) |
[Installation](https://github.com/omkarkhatavkar/testblame#2-installation) |
[Usage](https://github.com/omkarkhatavkar/testblame#3-usage) |
[Examples](https://github.com/omkarkhatavkar/testblame#4-examples) |
[ScreenShots](https://github.com/omkarkhatavkar/testblame#5-ScreenShots) |
[Contribution](https://github.com/omkarkhatavkar/testblame#6-contribution) |
[License](https://github.com/omkarkhatavkar/testblame#7-license) |
[Version](https://github.com/omkarkhatavkar/testblame#8-version) |



**About**

`testblame` is a cli tool that will gather all failed tests from Jenkins Junit report and provide you sorted report with a map of author and tests based on there git commit history for single and multiple authors. It also provides failed tests based on component or also tags.

By this tool, you can find out your own failed tests based in git commit from more than 500 failed tests. By this way, you will rid of a pain finding your own failed tests from JUnit test report and you do not have to remember your test.
 

## 1. Features

* Find out your own failed tests based on git commit history using GitHub email 
* Generate and send email report with a map of an author and failed tests based on git commit history 
* Generate and send email report with a map of an author and failed tests based on component JSON 
* See all failed tests 
* See all failed tests based in tags 


## 2. Installation

### 2.1 Linux/BSD
```shell
git clone https://github.com/omkarkhatavkar/testblame
cd testblame
sh setup.sh
```

## 3. Usage

### 3.1 Overview

To see all options with test blame, call the program without any arguments `testblame` on a console and see all help.  

```shell
$ testblame 

Usage: testblame [OPTIONS] COMMAND [ARGS]...

  This CLI tool to gather failed tests based on commit history

Options:
  --help  Show this message and exit.

Commands:
  refresh-config     Update config, pass new Jenkins test-result url
  send-email-report  Send an email report based on git commit history
  set-config         Set git_url and jenkins_url to collect the failed tests
  show-all-tests     Show all failed test names
  show-my-tests      Pass GitHub email to see failed tests
```

### 3.2 Set-Config TestBlame

`testblame set-config` command should be run as first, by that way testblame knows your Jenkins url to fetch failed tests and repo url from where to get git commit history. 
```shell
$ testblame set-config --help


Usage: testblame set-config [OPTIONS]

  Set git_url and jenkins_url to collect the failed tests

Options:
  --git-url TEXT      Pass the git url for test repo
  --jenkins-url TEXT  Pass the Jenkins url to collect the failed tests
  --help              Show this message and exit.
```
### 3.3 Show-My-Test TestBlame
`testblame show-my-test` will show only specific git hub user's failed tests based on git commit history
```shell
$ testblame show-my-test --help

Usage: testblame show-my-tests [OPTIONS]

  Pass GitHub email to see failed tests

Options:
  --local-repo TEXT  Provide test local repo if required
  --filter TEXT      Pass filter if local-repo is enabled
  --email TEXT       Pass email to get tests based on git commit history
  --skip TEXT        Pass search string to skip the specific tests
  --help             Show this message and exit.
```

### 3.3 Send-Email-Report TestBlame
 `testblame send-email-report` will send an email report with author and test map table based on git commit history or component-based JSON. Send emails are currently integrated with [SendGrid ](https://sendgrid.com/) 
 
 ```shell
$ testblame send-email-report --help

Usage: testblame send-email-report [OPTIONS]

  Send an email report based on git commit history

Options:
  --local-repo TEXT  Provide test local repo if required
  --email TEXT       Provide Email Report for Specific
  --skip TEXT        Pass search string to skip the specific tests
  --filter TEXT      Pass filter if local-repo is enabled
  --from_email TEXT  Pass from an email address
  --to_email TEXT    Pass to an email address
  --subject TEXT     Pass subject
  --component TEXT   pass JSON file path containing author and component tags
  --help             Show this message and exit.
```

## 4. Examples
Setting up testblame with configs such as git repo url and jenkins junit report url 
 ```shell
  testblame set-config --git-url="https://github.com/reponame" --jenkins-url="<host>/view/job/<jobname>/lastCompletedBuild/testReport/" 
  ```
Now once testblame knows repo and failed tests, time to know failed tests based on git-email-id

  ```shell
testblame show-my-tests --email="okhatavk"
Searching failed tests  [####################################]  100%          
tests.ui.testname_1 ⇒ Failed
tests.cli.testname_1 ⇒ Failed
  ```
Want to see only UI tests?
  ```shell
testblame show-my-tests --email="okhatavk" --skip=cli
Searching failed tests  [####################################]  100%          
tests.ui.testname_1 ⇒ Failed
  ```
Want to see only based on tag or filter or component?
  ```shell
testblame show-my-tests --email="okhatavk" --filter=dashboard
Searching failed tests  [####################################]  100%          
tests.cli.testname_dashboard_1 ⇒ Failed
tests.cli.testname_dashboard_2 ⇒ Failed
tests.cli.testname_dashboard_3 ⇒ Failed
  ```
  
  Generate and send email report for whole team based on git commit history ?
  ```shell
testblame send-email-report --from_email="testblame@testblame.com" --to_email="okhatavk@testblame.com" --subject="Testing Result Tier 1" 
  ```
   Generate and send email report for the whole team based on component.json?
  ```shell  
$ cat component.json 
{
  "Omkar": [
    "Test_1",
    "Test_10",
    "Test_11"
  ],
  "Rakesh": [
    "Test_2"
  ]
}
```
  ```shell
testblame send-email-report --from_email="testblame@testblame.com" --to_email="okhatavk@testblame.com" --subject="Testing Result Tier 1" --component.json
  ```
## 5. Screenshots

Showing some screenshots

![Screencast](https://raw.githubusercontent.com/omkarkhatavkar/testblame/master/doc/img/email_report.png)

## 6. Contribution
Contributions are welcome. Please check the  [issues](https://github.com/omkarkhatavkar/testblame/issues)  and feel free to open a pull request.

