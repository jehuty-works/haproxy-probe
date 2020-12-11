#!/bin/env python
 
 # URL='https://api.server.com'
 # RESULT=$(curl -k -L --output /dev/null --silent --show-error --write-out 'time_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}\ntime_appconnect: %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}' $URL)
 
 import sys
 import os 
 import csv
 import datetime 
 import json
 import subprocess
 import argparse
 from collections import OrderedDict
 from socket import gethostname, gethostbyname
 from time import sleep
 
 def get_args():
     """
     Parse CLI arguments (via sys.argv[]) and return arguments as a named tuple called 'Namespace'
     """
     parser = argparse.ArgumentParser()
 
     parser.add_argument(
         '--poll-time','-t',
         type=int,
         default=int(os.environ['POLL_TIME']),
         help='specify polling interval for curl')
 
     parser.add_argument(
         '--url','-u',
         type=str,
         help='specify remote URL')
 
     parser.add_argument(
         '--source-zone','-z',
         type=str,
         help='specify internal or external to openshift')
 
     parser.add_argument(
         '--f5-policy',
         type=str,
         default='',
         help='specify terminate, reencrypt, passthrough; default ""')
 
     parser.add_argument(
         '--haproxy-policy',
         type=str,
         default='',
         help='specify terminate, reencrypt, passthrough; default ""')
 
     parser.add_argument(
         '--description','-d',
         type=str,
         default='',
         help='specify terminate, reencrypt, passthrough; default ""')
 
     parser.add_argument(
         '--insecure','-k',
         action='store_true',
         default=False,
         help='tell script to ignore TLS validations')
 
     parser.add_argument(
         '--cacert',
         type=str,
         default=None,
         help='specify cacert bundle location; default uses built-in cert')
 
     # read specified file as search data 
     parser.add_argument(
         '-f','--file',
         type=str,
         default=sys.stdin,
         help='specify input file')
 
     # allow optional output file (over/write only), defaults to stdout
     parser.add_argument(
         '-o','--output',
         type=str,
         help='specify output file')
 
     parser.add_argument(
         '--version','-V',
         action='version', 
         version="""
             %(prog)s 1.1,
             Author: Aaron Robinett;
             Last Updated: 2020-08-10""")
 
     parsed_args = parser.parse_args()
 
     return parsed_args
 
 
 def process_data(parsed_args):
     """
     Build dataset of curl metrics and return OrderedDict()
     """
     args = parsed_args
 
     # store initial metrics in base_data
     base_data = OrderedDict()
     d = datetime.datetime.utcnow()
 
     base_data.update({
         "src_host": gethostname(), 
         "src_ip": gethostbyname(gethostname()), 
         "datetime": d.strftime('%Y-%m-%d %H:%M:%S')
     })
 
     # populate static metadata gathered from CLI or input file
     if args.url:
         base_data["remote_url"] = args.url
 
     if isinstance(args.source_zone, str) and args.source_zone.lower() in ['internal','external']:
         base_data["src_zone"] = args.source_zone
     else:
         base_data["src_zone"] = ''
 
     if isinstance(args.f5_policy, str) and args.f5_policy.lower() in ['reencrypt','terminate','passthrough','none']:
         base_data["f5_policy"] = args.f5_policy
     else:
         base_data["f5_policy"] = ''
 
     if isinstance(args.haproxy_policy, str) and args.haproxy_policy.lower() in ['reencrypt','terminate','passthrough','none']:
         base_data["haproxy_policy"] = args.haproxy_policy
     else:
         base_data["haproxy_policy"] = ''
 
     if isinstance(args.description, str):
         base_data["description"] = args.description
     else:
         base_data["description"] = ''
 
     # pass cacert from args if it exists, else default to local cert
     #curl_cacert = args.cacert if args.cacert else 'AllyCert.ca'
 
     # generate dict of curl output
     curl_data = parse_curl(curl_endpoint(args))
 
     # add curl output to existing dict
     base_data.update(curl_data)
 
     output = json.dumps(base_data, sort_keys=True)
     return output
 
 
 def curl_endpoint(parsed_args):
     """
     calls cURL in a sub-shell and returns the raw text output
     """
     args = parsed_args
 
     cmd_args = [
         'curl',
         '-L',
         '--output','/dev/null',
         '--silent', 
         '--show-error', 
         '--write-out', r'remote_ip: %{remote_ip}\nresponse_code: %{response_code}\nsslverify_result: %{ssl_verify_result}\ntime_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}\ntime_appconnect: %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}']
 
     # add additional curl args where needed:
     if args.cacert is not None:
         assert args.cacert, "TLS ERROR: --cacert requires a file name as an argument!"
         cmd_args.extend(['--cacert',str(args.cacert)])
     elif args.insecure and args.cacert is None:
         cmd_args.append('-k')
 
     # should be last:
     cmd_args.append(args.url)
 
     # create filehandle for /dev/null
     FNULL = open(os.devnull, 'w')
     # need to reuse output, so redirect stdout to PIPE
     proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=FNULL) 
     # reads from PIPE above
     output = proc.stdout.read()
     return output
 
 
 def parse_curl(curl_output):
     """
     parses raw string output from curl_endpoint and returns OrderedDict()
     """
     curl_data = OrderedDict()
     
     # each line has a standard format 'metric_name: value'
     # creating dictionary key-value pairs for each line
     curl_lines = curl_output.split("\n")
     for line in curl_lines:
         metric_key, metric_val = line.split(":")
         metric_key = metric_key.strip()
         metric_val = metric_val.strip()
         curl_data.update({metric_key: metric_val})
 
     return curl_data
 
 def process_by_csv(parsed_args):
     args = parsed_args
 
     with open(args.file, 'r') as fh:
         csvreader = csv.DictReader(fh)
 
         for row in csvreader:
             args.url = row['URL']
             args.source_zone = row['SRC_ZONE']
             args.f5_policy = row['F5_POLICY']
             args.haproxy_policy = row['HAPROXY_POLICY']
             args.description = row['DESCRIPTION']
             print(process_data(args))
 
 if __name__ == '__main__':
     args = get_args()
     if isinstance(args.file, str): # check to see if --file has been passed, will be sys.stdin if not
         while True:
             process_by_csv(args)
             sleep(args.poll_time)
     else:
         print("Running in standalone mode...\n")
         print(process_data(args))
