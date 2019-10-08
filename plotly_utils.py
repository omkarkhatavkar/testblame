import chart_studio
import os

import json
import requests
from requests.auth import HTTPBasicAuth


def get_pages(username, page_size, auth, headers):
    url = 'https://api.plot.ly/v2/folders/all?user='+username+'&page_size='+str(page_size)
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code != 200:
        return
    page = json.loads(response.content.decode('utf-8'))
    yield page
    while True:
        resource = page['children']['next']
        if not resource:
            break
        response = requests.get(resource, auth=auth, headers=headers)
        if response.status_code != 200:
            break
        page = json.loads(response.content.decode('utf-8'))
        yield page


def permanently_delete_files(username, auth, headers, page_size=500, filetype_to_delete='plot'):
    for page in get_pages(username, page_size, auth, headers):
        for x in range(0, len(page['children']['results'])):
            fid = page['children']['results'][x]['fid']
            res = requests.get('https://api.plot.ly/v2/files/' + fid, auth=auth, headers=headers)
            res.raise_for_status()
            if res.status_code == 200:
                json_res = json.loads(res.content.decode('utf-8'))
                if json_res['filetype'] == filetype_to_delete:
                    # move to trash
                    requests.post('https://api.plot.ly/v2/files/'+fid+'/trash', auth=auth, headers=headers)
                    # permanently delete
                    requests.delete('https://api.plot.ly/v2/files/'+fid+'/permanent_delete', auth=auth, headers=headers)


def delete_all_earlier_charts():
    username = 'testblame'
    api_key = os.environ['API_KEY']
    auth = HTTPBasicAuth(username, api_key)
    headers = {'Plotly-Client-Platform': 'python'}
    chart_studio.tools.set_credentials_file(username=username, api_key=api_key)
    permanently_delete_files(username, filetype_to_delete='plot', auth=auth, headers=headers)
    permanently_delete_files(username, filetype_to_delete='plot', auth=auth, headers=headers)

