import argparse
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

def get_input():
    parser = argparse.ArgumentParser(description='Work with Github')
    parser.add_argument('-u', '--user', dest='user',
                        help='Github User Name')
    parser.add_argument('-p', '--password', dest='password',
                        help='Github Password')
    parser.add_argument('-t', '--type', dest='type', default="issues",
                        help='Type of action(issues)')
    parser.add_argument('-d', '--days', dest='days', default=1, type=int,
                        help='time range of the action')
    parser.add_argument('-e', '--extra', dest='extra',
                        help='extra prameters append to endpoint')
    parser.add_argument('-w', '--withurl', dest='withurl', default=False, action="store_true",
                        help='whether append url')

    args = parser.parse_args()
    user, password, type, days = args.user, args.password, args.type, args.days
    extra = args.extra
    withurl = args.withurl
    if user is None or password is None or type is None or days is None:
        print "user, password, type, days cannot be None"
        parser.print_help()
        return None
    d = dict(user=user, password=password, type=type, days=days, extra=extra, withurl=withurl)
    return d

class Github(object):
    def __init__(self, data):
        self.data = data
        self.set_endpoint()

    def set_endpoint(self):
        self.endpoint = ""

    def request(self):
        if self.data is None:
            return
        result = self._call_api()
        parsed_result = self._parse_result(result)
        return self.pprint(parsed_result)

    def _parse_result(self, result):
        out = []
        for item in result:
            ID = item.get("number")
            url = item.get("url")
            title = item.get("title")
            created_at = item.get("created_at")
            closed_at = item.get("closed_at")
            out.append(dict(ID=ID, url=url, title=title, created_at=created_at, closed_at=closed_at))
        return out

    def pprint(self, out):
        return out

    def _call_api(self):
        #import pdb;pdb.set_trace()
        user = self.data.get("user")
        password = self.data.get("password")
        r = requests.get(self.endpoint, auth=HTTPBasicAuth(user, password))
        return r.json()

class GithubIssue(Github):
    def set_endpoint(self):
        self.endpoint = "https://api.github.com/repos/Knozen/API/issues"
        extra = self.data.get("extra")
        user = self.data.get("user")
        days = self.data.get("days")
        since = datetime.now() - timedelta(days=days)
        sincestr = since.isoformat()
        
        if extra:
            self.endpoint += '''?assignee={}&state={}&since={}'''.format(user, extra, sincestr)
        print self.endpoint

    def pprint(self, out):
        ret = ""
        extra = self.data.get("extra")
        withurl = self.data.get("withurl")
        word = "Fixed" if extra == "closed" else "Working on"
        append = "-{url}" if withurl else ""
        tpl = word + " #{ID} ({title})" + append + "\n"
        for item in out:
            ret += tpl.format(**item)
        return ret
    
if __name__ == "__main__":
    data = get_input()
    g = GithubIssue(data)
    print g.request()
