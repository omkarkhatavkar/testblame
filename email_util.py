# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail
import re
import plotly.plotly as py
import plotly.graph_objs as go
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_utils import (
    get_test_history,
    set_test_fail_reason,
    get_dynamic_graph_history
    )


def send_email(from_email, to_email, subject, content):
    try:
        if os.environ.get('SMTP_SERVER_NAME') and os.environ.get('SMTP_SERVER_PORT'):
            smtpobj = smtplib.SMTP(os.environ['SMTP_SERVER_NAME'],
                                   os.environ['SMTP_SERVER_PORT'])
            msg = MIMEMultipart("alternative")
            msg['Subject'] = subject
            msg['From'] = from_email
            to_email = to_email.strip().split(',')
            msg['To'] = ', '.join(to_email)
            attachment = MIMEText(content, "html")
            msg.attach(attachment)
            smtpobj.sendmail(from_email, to_email, msg.as_string())
            print("Email Sent Successfully ")
        elif os.environ.get('SENDGRID_API_KEY'):
            sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email(from_email)
            to_email = Email(to_email)
            content = Content("text/html", content)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print("Email Sent Successfully ")
        else:
            print("Failed to Send Email, Some Settings/Options are missing !")
    except Exception as err:
        print(err)


def save_email_content(html):
    # open file with *.html* extension to write html
    file = open("email.html", "w")
    # write then close file
    file.write(html)
    file.close()


def get_matched_jenkins_url(test, url_map):
    for key, values in url_map.items():
        if test in values:
            index = re.findall('\d.*', key)[0]
            return url_map['jenkins_url_{}'.format(index)]


def if_test_is_parametrize(test):
    if '[' and ']' in test:
        test = str(test).replace('[', '_').replace(']', '_')
    return test


def make_tests_linkable(test_list, url):
    """This function make test linkable and very specific to
    robottelo test suite.
    """
    test_list_links = ''
    for test in test_list:
        test_url = (get_matched_jenkins_url(test, url_map=url))
        test = if_test_is_parametrize(test)
        test_split = test.split('.')
        reason_url = "{0}{1}/{2}/{3}".format(test_url,
                                             '.'.join(test_split[:-2]),
                                             "".join(test_split[-2:-1]),
                                             ''.join(test_split[-1:]))

        test_link = '</br><a href="{0}{1}/{2}/{3}" target="_blank">{4}</a></br>'. \
            format(test_url, '.'.join(test_split[:-2]), "".join(test_split[-2:-1]),
                   "".join(test_split[-1:]), test)
        test_list_links += test_link
        # set_test_fail_reason(reason_url)
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


def building_graph(content, bar_chart, pie_chart, dynamic_graph = None):
    data = [go.Bar(
        x=list(bar_chart.keys()),
        y=list(bar_chart.values()),
        hoverinfo='x+y'
    )]
    data_2 = [go.Pie(
        labels=[label.upper() for label in pie_chart.keys()],
        values=[value for value in pie_chart.values()],
        textinfo='value',
        hoverinfo='label+percent'
    )]
    most_failed = sorted((value, key) for (key, value) in bar_chart.items())
    most_failed = most_failed[-10:]
    most_failed_data = [go.Bar(
        x=list([key[1] for key in most_failed]),
        y=list([value[0] for value in most_failed]),
        hoverinfo='x+y'
    )]

    unique_id_bar_chart = uuid.uuid4()
    unique_id_pie_chart = uuid.uuid4()
    unique_id_most_failed_chart = uuid.uuid4()
    graph_url_1 = py.plot(data, auto_open=False, filename='email-report-graph-1-{}'.format(unique_id_bar_chart))
    graph_url_2 = py.plot(data_2, auto_open=False, filename='email-report-graph-1-{}'.format(unique_id_pie_chart))
    graph_url_3 = py.plot(most_failed_data, auto_open=False, filename='email-report-graph-1-{}'.
                          format(unique_id_most_failed_chart))

    graph_url_1_image = os.path.splitext(graph_url_1)[0]+".png"
    graph_url_2_image = os.path.splitext(graph_url_2)[0] + ".png"
    graph_url_3_image = os.path.splitext(graph_url_3)[0] + ".png"
    email_content = content.replace('<=graph_url_1=>', graph_url_1)
    email_content = email_content.replace('<=graph_url_2=>', graph_url_2)
    email_content = email_content.replace('<=graph_url_3=>', graph_url_3)
    email_content = email_content.replace('<=graph_url_1_image=>', graph_url_1_image)
    email_content = email_content.replace('<=graph_url_2_image=>', graph_url_2_image)
    email_content = email_content.replace('<=graph_url_3_image=>', graph_url_3_image)
    test_history = get_test_history()
    if dynamic_graph is not None:
        pattern, graph_name = str(dynamic_graph).split(',')
        test_history1 = get_dynamic_graph_history(pattern=pattern)
        dynamic_trend = [go.Scatter(
            x=[i[0] for i in test_history1],
            y=[i[1] for i in test_history1],
        )]
        unique_id_line_chart_1 = uuid.uuid4()
        graph_url_5 = py.plot(dynamic_trend, auto_open=False, filename='email-report-graph-1-{}'.
                              format(unique_id_line_chart_1))
        graph_url_5_image = os.path.splitext(graph_url_5)[0] + ".png"
        email_content = email_content.replace('<=graph_url_5=>', graph_url_5)
        email_content = email_content.replace('<=graph_url_5_image=>', graph_url_5_image)
    if get_test_history() is not None:
        unique_id_line_chart = uuid.uuid4()
        trend = [go.Scatter(
            x=[i[0] for i in test_history],
            y=[i[1] for i in test_history],
        )]
        graph_url_4 = py.plot(trend, auto_open=False, filename='email-report-graph-1-{}'.
                              format(unique_id_line_chart))
        graph_url_4_image = os.path.splitext(graph_url_4)[0] + ".png"
        email_content = email_content.replace('<=graph_url_4=>', graph_url_4)
        email_content = email_content.replace('<=graph_url_4_image=>', graph_url_4_image)
    save_email_content(email_content)
    return email_content
