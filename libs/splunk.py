import requests, time

class Splunk:
    def __init__(self, url, token) -> None:
        self.url = url + '/services/search/v2/jobs'
        self.token = token
        self.spl_headers = {'Authorization': 'Bearer {}'.format(token)}
        self.output_mode = 'output_mode=json'

    def search(self, search_query, start_time, end_time, timezone):
        create_search = self.create_search(search_query, start_time, end_time, timezone)
        job_id = create_search['sid']
        search_status = self.search_status(job_id)
        events = self.search_results(job_id)
        if events:
            csv_header = list(events[0].keys())
        else:
            csv_header = ''
        search_results = {'csv_header': csv_header, 'events': events, 'count': len(events)}
        return search_results

    def create_search(self, search_query, start_time, end_time, timezone):
        url = self.url + '?' + self.output_mode
        payload = 'search=search%20{}&earliest={}&latest={}'.format(search_query, start_time, end_time)
        create_search_job = requests.post(url, headers=self.spl_headers, data=payload)
        if create_search_job.status_code == 201:
            return create_search_job.json()
        else:
            return {}

    def search_status(self, job_id):
        endpoint = '/{}?{}'.format(job_id, self.output_mode)
        loop_condition = True
        while loop_condition:
            job_search_status = requests.get(self.url + endpoint, headers=self.spl_headers)
            status_code = job_search_status.status_code
            status_data = job_search_status.json()
            state = status_data['entry'][0]['content']['dispatchState']
            if status_code == 200 and state == 'DONE':
                loop_condition = False
                return {'status': 'complete'}
            elif status_code == 200 and state in ['INTERNAL_CANCEL', 'USER_CANCEL', 'BAD_INPUT_CANCEL', 'QUIT', 'FAILED']:
                loop_condition = False
                return {'status': 'failed'}
            else:
                time.sleep(10)
                continue

    def search_results(self, job_id):
        offset_value = 0
        limit = 10000
        loop_condition = True
        result = []
        while loop_condition:
            endpoint = '/{}/results?{}&count={}&offset={}'.format(job_id, self.output_mode, limit, offset_value)
            results = requests.get(self.url + endpoint, headers=self.spl_headers)
            data = results.json()
            if len(data['results']) == 0:
                loop_condition = False
            else:
                offset_value = offset_value + len(data['results'])
                for record in data['results']:
                    result.append(record)
        return result