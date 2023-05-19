import requests, time

class SumoLogic:
    def __init__(self, _url, _access_id, _access_key) -> None:
        self.url = _url
        self.access_id = _access_id
        self.access_key = _access_key
        self.sl_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.result = []

    def search(self, search_query, start_time, end_time, timezone):
        create_search = self.create_search(search_query, start_time, end_time, timezone)
        job_id = create_search['id']
        search_status = self.search_status(job_id)
        events = self.search_results(job_id)
        if events:
            csv_header = list(events[0].keys())
        else:
            csv_header = ''
        search_results = {'csv_header': csv_header, 'events': events, 'count': len(events)}
        return search_results

    def create_search(self, search_query, start_time, end_time, timezone):
        payload = '{"query": "' + search_query + '", "from": "' + start_time + '", "to": "' + end_time + '", "timeZone": "' + timezone + '"}'
        create_search_job = requests.post(self.url, auth=(self.access_id, self.access_key), headers=self.sl_headers, data=payload)
        if create_search_job.status_code == 202:
            return create_search_job.json()
        else:
            return {}

    def search_status(self, job_id):
        endpoint = '/{}'.format(job_id)
        loop_condition = True
        while loop_condition:
            job_search_status = requests.get(self.url + endpoint, auth=(self.access_id, self.access_key), headers=self.sl_headers)
            status_code = job_search_status.status_code
            status_data = job_search_status.json()
            if status_code == 200 and status_data['state'] == 'DONE GATHERING RESULTS':
                loop_condition = False
                return {'status': 'complete'}
            elif status_code == 200 and (status_data['state'] == 'FORCE PAUSED' or status_data['state'] == 'CANCELLED'):
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
            endpoint = '/{}/messages?offset={}&limit={}'.format(job_id, offset_value, limit)
            results = requests.get(self.url + endpoint, auth=(self.access_id, self.access_key), headers=self.sl_headers)
            data = results.json()
            if len(data['messages']) == 0:
                loop_condition = False
            else:
                offset_value = offset_value + len(data['messages'])
                for record in data['messages']:
                    result.append(record['map'])
        return result