# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail
import re
import plotly.plotly as py
import plotly.graph_objs as go
import uuid


def send_email(from_email, to_email, subject, content):
    try:
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('+'))
        from_email = Email(from_email)
        to_email = Email(to_email)
        content = Content("text/html", content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
    except Exception as err:
        print(err)


def save_email_content(html):
    # open file with *.html* extension to write html
    file = open("email.html", "w")
    # write then close file
    file.write(html)
    file.close()


def make_tests_linkable(test_list, url):
    """This function make test linkable and very specific to
    robottelo test suite.
    """
    test_list_links = ''
    for test in test_list:
        test_split = test.split('.')
        test_link = '</br><a href="{0}{1}/{2}/{3}" target="_blank">{4}</a></br>'. \
            format(url, '.'.join(test_split[:-2]), "".join(test_split[-2:-1]),
                   "".join(test_split[-1:]), test)
        test_list_links += test_link
    return test_list_links


def get_file_content(file_path):
    with open(file_path, 'r') as my_file:
        return my_file.read()


def build_content(tests, jenkins_url, with_link):
    email_content = get_file_content('email_template')
    content = ""
    if isinstance(tests, dict):
        for author, test_list in tests.items():
            if '@' in author:
                author = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", author)[0]
            author_col = "<tr><td>{0}</td>".format(author)
            if with_link is None:
                table = author_col + "<td class=myclass>"+"<br/><br/>".join(test_list)
            else:
                test_col = "<td class=myclass>"
                table = author_col + test_col + make_tests_linkable(test_list, jenkins_url)
            content = content + table + "</td></tr>"
    email_content = email_content.replace('<=Report=>', content)
    save_email_content(email_content)
    return email_content


def building_graph(content, tags):
    data = [go.Bar(
        x=list(tags.keys()),
        y=list(tags.values()),
    )]
    unique_id = uuid.uuid4()
    graph_url_1 = py.plot(data, auto_open=False, filename='email-report-graph-1-{}'.format(unique_id))
    graph_url_1_image = os.path.splitext(graph_url_1)[0]+".png"
    email_content = content.replace('<=graph_url_1=>', graph_url_1)
    email_content = email_content.replace('<=graph_url_1_image=>', graph_url_1_image)
    save_email_content(email_content)
    return email_content
