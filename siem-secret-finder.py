#!/usr/bin/python
import yaml, csv, sys, re
from libs.sumoLogic import SumoLogic
from libs.siemSecretFinder import SiemSecretFinder
from libs.splunk import Splunk
import nltk
from nltk.corpus import words

# Write results to csv file
def csv_writer(_siem, _secrets, _output_file_path, _csv_header):
    _csv_header = _csv_header + ['keyword', 'secret']
    with open(_output_file_path, 'w+') as f:
        if _siem == 'sumologic':
            csv_writer = csv.DictWriter(f, _csv_header)
        elif _siem == 'splunk':
            csv_writer = csv.DictWriter(f, _csv_header)
        else:
            pass
        csv_writer.writeheader()
        csv_writer.writerows(_secrets)

if __name__ == '__main__':

    # Print banner 
    print('''\u001b[36m
█████████████████████████████████████████████████████████████████████████████████████████████████████
█─▄▄▄▄█▄─▄█▄─▄▄─█▄─▀█▀─▄███─▄▄▄▄█▄─▄▄─█─▄▄▄─█▄─▄▄▀█▄─▄▄─█─▄─▄─███▄─▄▄─█▄─▄█▄─▀█▄─▄█▄─▄▄▀█▄─▄▄─█▄─▄▄▀█
█▄▄▄▄─██─███─▄█▀██─█▄█─████▄▄▄▄─██─▄█▀█─███▀██─▄─▄██─▄█▀███─██████─▄████─███─█▄▀─███─██─██─▄█▀██─▄─▄█
▀▄▄▄▄▄▀▄▄▄▀▄▄▄▄▄▀▄▄▄▀▄▄▄▀▀▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▀▄▄▄▀▀▀▀▄▄▄▀▀▀▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▀▀▄▄▄▄▄▀▄▄▀▄▄▀\u001b[37m''')

    # Download english words using nltk library 
    nltk.download('words', quiet=True)
    english_words = set(words.words())
    
    # Read config file 
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    color_white = '\u001b[37m'
    color_green = '\u001b[32m'
    color_red = '\u001b[31m'
    line_override = '\033[F\033[K'

    # Read from config file 
    siem = config['secret-finder']['siem'].lower()
    regex_keywords = config['secret-finder']['regex_keywords']
    regex_keywords = '|'.join(regex_keywords) # Regex pattern 
    output_file_path = config['secret-finder']['output_file_path']
    thread_count = int(config['secret-finder']['thread_count'])
    ignore_secret_values = config['secret-finder']['ignore_secret_values']

    if siem == 'sumologic':
        url = re.sub('/$', '', config['sumologic']['url']) # Remove '/' from end of the string 
        access_id = config['sumologic']['access_id']
        access_key = config['sumologic']['access_key']
        search_query = config['sumologic']['search_query']
        start_time = config['sumologic']['start_time']
        end_time = config['sumologic']['end_time']
        timezone = config['sumologic']['timezone']

        print("\nSearch query: {}{}{}".format(color_green, search_query, color_white))
        print("Search timeframe: {}{} - {}{}".format(color_green, start_time, end_time, color_white))
        print("Search status: In progress")
        search_results = SumoLogic(url, access_id, access_key).search(search_query, start_time, end_time, timezone)
        print("{}Search status: {}Complete{}".format(line_override, color_green, color_white))
        print("No. of events: {}{}{}".format(color_green, search_results['count'], color_white))
        if search_results['count'] > 0:
            csv_header = search_results['csv_header']
            print("Secrets finder: In progress")
            secrets = SiemSecretFinder(regex_keywords, thread_count, ignore_secret_values).search(search_results['events'], english_words)
            print("{}Secrets finder status: {}Complete{}".format(line_override, color_green, color_white))
            print("No. of secrets: {}{}{}\n".format(color_green, len(secrets), color_white))
        else:
            secrets = []
    elif config['secret-finder']['siem'] == 'splunk':
        url = re.sub('/$', '', config['splunk']['url'])
        token = config['splunk']['token']
        search_query = config['splunk']['search_query']
        start_time = config['splunk']['start_time']
        end_time = config['splunk']['end_time']
        timezone = config['splunk']['timezone']
        print("\nSearch query: {}{}{}".format(color_green, search_query, color_white))
        print("Search timeframe: {}{} - {}{}".format(color_green, start_time, end_time, color_white))
        print("Search status: In progress")
        search_results = Splunk(url, token).search(search_query, start_time, end_time, timezone)
        print("{}Search status: {}Complete{}".format(line_override, color_green, color_white))
        print("No. of events: {}{}{}".format(color_green, search_results['count'], color_white))
        if search_results['count'] > 0:
            csv_header = search_results['csv_header']
            print("Secrets finder: In progress")
            secrets = SiemSecretFinder(regex_keywords, thread_count, ignore_secret_values).search(search_results['events'], english_words)
            print("{}Secrets finder status: {}Complete{}".format(line_override, color_green, color_white))
            print("No. of secrets: {}{}{}\n".format(color_green, len(secrets), color_white))
        else:
            secrets = []
    else:
        print('\n{}: {}No config found{}\n'.format(siem, color_red, color_white))
        sys.exit()

    # Do not write to csv if result set is empty 
    if len(secrets) > 0:
        csv_writer(siem, secrets, output_file_path, csv_header)
        print("{}Output file: {}{}{}\n".format(line_override, color_green, output_file_path, color_white))