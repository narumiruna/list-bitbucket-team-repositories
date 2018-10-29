import argparse
import http

import requests
from bs4 import BeautifulSoup


def load_txt(f):
    with open(f, 'r') as fp:
        return fp.read()


def get_cookies(raw_cookies):
    cookies = http.cookies.SimpleCookie()
    cookies.load(raw_cookies)
    return {k: v.value for k, v in cookies.items()}


def write_lines(lines, f):
    with open(f, 'w') as fp:
        fp.write('\n'.join(lines))


def list_team_repo(team, cookies):
    repos = []

    page = 1
    while True:
        url = 'https://bitbucket.org/{}/?page={}'.format(team, page)
        res = get_repos(url, cookies)

        if len(res) == 0:
            break

        repos += res
        page += 1

    return repos


def get_repos(url, cookies):
    res = []
    print('Get repositories from {}'.format(url))

    with requests.session() as sess:
        r = sess.get(url, cookies=cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        repos = soup.find_all(
            'a', attrs={'class': 'execute repo-list--repo-name'})

        print('Found {} repositories'.format(len(repos)))

        for repo in repos:
            repo_link = repo.get('href')  # /team/repo
            repo_name = repo_link[1:]  # team/repo
            res.append('git@bitbucket.org:{}.git'.format(repo_name))

    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--team', type=str, default='teamname')
    parser.add_argument('-c', '--cookie', type=str, default='raw_cookies.txt')
    parser.add_argument('-o', '--output', type=str, default='repositories.txt')
    args = parser.parse_args()

    raw_cookies = load_txt(args.cookie)
    cookies = get_cookies(raw_cookies)

    repos = list_team_repo(args.team, cookies)

    write_lines(repos, args.output)


if __name__ == '__main__':
    main()
