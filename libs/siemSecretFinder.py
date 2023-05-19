import re
import threading, queue

class SiemSecretFinder:
    def __init__(self, regex_keywords, thread_count, ignore_secret_values) -> None:
        self.results = []
        self.end_process = False # To control worker thread 
        self.regex_keywords = regex_keywords
        self.thread_count = thread_count
        self.ignore_secret_values = [''] + ignore_secret_values

    def regex_match(self, record):
        pattern = r'({})'.format(self.regex_keywords) + r'((\s+|\=|\"|\'|\:\:|\>|\:|\{)*)([^(\s+|\=|\"|\'|\<|\:\:|\>|\:|\,)*)]+)((\s+|\=|\"|\'|\<|\:\:|\>|\:|\,|\})*)'
        regex_match = re.findall(pattern, record.replace('\\', ''), flags=re.IGNORECASE)
        return regex_match

    def search(self, records, english_words):
        self.search_secrets(records, english_words)
        return self.results

    def search_secrets(self, records, english_words):
        # Threading
        try:
            work = queue.Queue()
            threads = []
            def worker():
                while not self.end_process:                    
                    try:
                        job = work.get(True, 5)
                        regex_output = self.regex_match(job['_raw'])
                        if len(regex_output) > 0:
                            for i in range(len(regex_output)):
                                keyword = regex_output[i][0]
                                keyword_separator = regex_output[i][1]
                                secret = regex_output[i][3]
                                secret_separator = regex_output[i][4]
                                if keyword_separator != '' and secret not in self.ignore_secret_values:
                                    if not secret in english_words:
                                        job['keyword'] = keyword
                                        job['secret'] = secret
                                        self.results.append(job)
                    except queue.Empty:
                        break

                    work.task_done()

            # Assign a job to worker Queue
            if records:
                for i in range(len(records)):
                    records[i]['_raw'] = records[i]['_raw'].replace('\n', '')
                    work.put(records[i])
            
            # Append the worker Queue jobs to thread
            for unused_index in range(self.thread_count):
                thread = threading.Thread(target=worker)
                thread.daemon = True
                thread.start()
                threads.append(thread)

            for thread in threads:
                if thread.is_alive():
                    thread.join()

        except Exception as err:
            print('INFO - Queue init error : {}'.format(err))
            self.end_process = True
            for thread in threads:
                if thread.is_alive():
                    thread.join()
        