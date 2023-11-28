from __future__ import print_function
import argparse

parser = argparse.ArgumentParser(description='cmdArgs')
parser.add_argument('donnees.csv', type=str, default='slack_data.csv',
                help='filename to write analysis output in CSV format')
parser.add_argument('C:\Users\TCHANDO\network_analysis\', required=True, type=str, help='directory where slack data reside')
parser.add_argument('all-week5', type=str, default='', help='which channel we parsing')
parser.add_argument('--userfile', type=str, default='users.json', help='users profile information')

cfg = parser.parse_args()
# print(cfg)