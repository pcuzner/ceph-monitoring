#!/usr/bin/env python3

# Examples
# ./extract-panels.py --grafana http://e23-h29-740xd.alias.bos.scalelab.redhat.com:3000 --proxy http://192.168.122.2:3128
# ./extract-panels.py --grafana http://e23-h29-740xd.alias.bos.scalelab.redhat.com:3000 --proxy http://192.168.122.2:3128 --mode extract
# ./extract-panels.py --grafana http://e23-h29-740xd.alias.bos.scalelab.redhat.com:3000 --proxy http://192.168.122.2:3128 --panel-uid 9b21149a-1be9-4264-ba9f-cf3cf49249a2

import os
import sys
import json
import requests
from urllib.parse import urlparse

import argparse

default_mode = "list"
default_dir = "panels"


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["list", "extract"], default=default_mode, help=f"operation mode of the tool (default={default_mode})")
    parser.add_argument("--panel-uid", type=str, default="ALL", help="UID of the panel to extract from Grafana")
    parser.add_argument("--grafana", dest="grafana_url", type=str, required=True, help="URL of Grafana (including http/https prefix)")
    parser.add_argument("--proxy", dest="proxy_url", type=str, help="URL of a proxy to use to access Grafana")
    parser.add_argument("--proxy-user",type=str, default="", help="username for proxy access [optional]")
    parser.add_argument("--proxy-password",type=str, default="", help="password for proxy access [optional]")
    parser.add_argument("--output-dir", type=str, default=default_dir, help=f"Output directory for panels(default={default_dir})")

    return parser.parse_args()


def _build_fname(panel):
    fname = f"{panel['name'].replace(' ', '_')}.json"
    fname = fname.replace('/', '')
    return fname


def _build_proxy(args):
    if not args.proxy_url:
        return {}
    
    proxy_credentials = ""
    if args.proxy_user:
        proxy_credentials = f"{args.proxy_user}:{args.proxy_password}@"
    res = urlparse(args.proxy_url)
    
    return {
        res.scheme: f"{proxy_credentials}{res.netloc}"
    }


def list_panels(args):
    print("Listing all library panel names")
    library_element_api = f"{args.grafana_url}/api/library-elements"
    proxy = _build_proxy(args)
    resp = requests.get(library_element_api, proxies=proxy)
    if resp.status_code != 200:
        print("Unable to access Grafana: ", resp.status_code)
        sys.exit(8)

    js = resp.json()
    print(js.keys())
    elements = js['result']['elements']
    print(f"Found {len(elements)} library panels")
    for panel in elements:
        print(f"{panel['uid']} ... {panel['name']}")

def _dump_panel(panel):
    fname = _build_fname(panel)
    print(f"Writing {fname} to {args.output_dir}")
    with open(os.path.join(args.output_dir, fname), "w") as f:
        f.write(json.dumps(panel, indent=2))

def extract_panels(args):
    if args.panel_uid != "ALL":

        print(f"Fetching panel with uid of {args.panel_uid}")
        library_element_api = f"{args.grafana_url}/api/library-elements/{args.panel_uid}"
        proxy = _build_proxy(args)
        resp = requests.get(library_element_api, proxies=proxy)
        if resp.status_code != 200:
            print("Unable to access Grafana: ", resp.status_code)
            sys.exit(8)

        js = resp.json()
        panel = js['result']
        _dump_panel(panel)
    else:
        print(f"Dumping all library panel to {args.output_dir}")
        library_element_api = f"{args.grafana_url}/api/library-elements"
        proxy = _build_proxy(args)
        resp = requests.get(library_element_api, proxies=proxy)
        if resp.status_code != 200:
            print("Unable to access Grafana: ", resp.status_code)
            sys.exit(8)

        js = resp.json()
        result = js['result']
        elements = result['elements']
        for panel in elements:
            _dump_panel(panel)



def _parse_url(url_string):

    errs = []
    try:
        res = urlparse(url_string)
    except:
        return False, []
    if res.scheme not in ['http', 'https']:
        errs.append("url scheme must be either http or https")
    if res.netloc:
        host_fragments = res.netloc.split(":")
        if len(host_fragments) == 2:
            if not host_fragments[1].isnumeric():
                errs.append("port is not a number")
        else:
            errs.append("host is missing port number")
        pass
    else:
        errs.append("invalid host:port")
    
    return len(errs) == 0, errs


def valid_args(args):
    def _print_errs(errs):
        for e in errs:
            print(f"\t- {e}")

    args_ok = True

    valid, errs = _parse_url(args.grafana_url)
    if not valid:
        print("grafana url is invalid")
        _print_errs(errs)
        args_ok = False

    if args.proxy_url:
        valid, errs = _parse_url(args.proxy_url)
        if not valid:
            print("proxy url is invalid")
            _print_errs(errs)
            args_ok = False

    if (args.proxy_user and not args.proxy_password) or \
        (args.proxy_password and not args.proxy_user):
        print("incomplete proxy credentials")
        args_ok = False

    return args_ok


def main(args):

    if not valid_args(args):
        print("Aborting")
        sys.exit(4)

    if args.panel_uid != "ALL":
        args.mode = "extract"

    if args.mode == "list":
        list_panels(args)
    elif args.mode == "extract":
        if "/" not in args.output_dir:
            args.output_dir = os.path.join(os.getcwd(), args.output_dir)
        if not os.path.exists(args.output_dir):
            print(f"Creating directory {args.output_dir}")
            os.mkdir(args.output_dir)

        extract_panels(args)
    

if __name__ == "__main__":
    args = parser()

    main(args)
