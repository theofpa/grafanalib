"""Tools for maintaining Grafana datasources."""

import argparse
import attr
import requests
import sys
from urllib.parse import ParseResult, urlparse


@attr.s
class BasicAuthCredentials(object):
    username = attr.ib()
    password = attr.ib()

    def to_json_dict(self):
        return {
            'basicAuth': True,
            'basicAuthUser': self.username,
            'basicAuthPassword': self.password
        }


@attr.s
class DataSource(object):
    name = attr.ib()
    type = attr.ib()
    url = attr.ib()
    access = attr.ib()
    credentials = attr.ib()

    def to_json_dict(self):
        data = {
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'access': self.access,
        }
        if self.credentials:
            data.update(self.credentials)
        return data


@attr.s
class GrafanaAPI(object):

    base_url = attr.ib()
    credentials = attr.ib()

    def _get_session(self):
        if not self.credentials:
            return requests.Session()
        return requests.Session(
            auth=(self.credentials.username, self.credentials.password))

    def update_datasource(self, data_source):
        return self._get_session().post(
            '/'.join([self.base_url, 'datasource']),
            json=data_source.to_json_dict())


def make_parser():
    parser = argparse.ArgumentParser(prog='gfdatasource')
    parser.add_argument(
        'grafana-url', type=urlparse,
        default='http',
        help="URL of Grafana API",
    )
    parser.add_argument(
        'data-source-url', type=urlparse,
        help="URL of data source",
    )
    parser.add_argument(
        'access', type=str, default='proxy',
        help="Type of access used by Grafana to the data source",
    )
    parser.add_argument(
        'type', type=str, default='prometheus',
        help="The type of data source",
    )
    parser.add_argument(
        'name', type=str, default='Prometheus',
        help="The name of the data source",
    )
    return parser


def _split_creds(url):
    creds = BasicAuthCredentials(url.username, url.password)
    netloc = url.netloc.split('@')[1] if '@' in url.netloc else url.netloc
    url = ParseResult(
        scheme=url.scheme,
        netloc=netloc,
        path=url.path,
        params=url.params,
        query=url.query,
        fragment=url.fragment,
    )
    return url, creds


def main():
    parser = make_parser()
    opts = parser.parse_args(sys.argv[1:])
    grafana_url, grafana_creds = _split_creds(opts.grafana_url)
    datasource_url, datasource_creds = _split_creds(opts.data_source_url)
    
