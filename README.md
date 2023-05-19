# SIEM Secret Finder 

## About The Project

Ensuring the confidentiality of secrets and limiting access to only authorized individuals or services is absolutely critical. However, the secrets accidentally leak through configuration files, databases, or logging messages. Therefore, it's essential to take all necessary precautions.

The SIEM secret finder is an excellent solution to tackle this issue. It uses keyword and pattern matching to search for specific words and patterns that are commonly associated with secrets, such as API key, password, token, and private key. Once a potential secret is identified, the tool eliminates false positives using language processing libraries. The secret finder has built-in integration with Splunk & Sumologic solutions and can be easily integrated with other SIEM solutions. 

![siem-secret-finder](https://github.com/govindasamyarun/siem-secret-finder/assets/69586504/8fd91043-8908-4536-a408-c7937c9d9041)

## Integrations

* Splunk
* Sumologic

## Getting started

1. Clone the repository

   ```sh
   cd /Data
   git clone https://github.com/govindasamyarun/siem-secret-finder
   ```

2. Install prerequisites 

* pip install -r requirements.txt

3. Update the config.yaml file. The following are the mandatory values. 

```yaml
    secret-finder:
        siem: <<Splunk|Sumologic>>
        output_file_path: '/tmp/secrets.csv'

    sumologic:
        url: 'https://<<hostname>>/api/v1/search/jobs'
        access_id: '<<acess_id>>'
        access_key: '<<access_key>>'
        search_query: '_dataTier=All _source=* access_token or privateKey or publicKey | fields _raw'
        start_time: '2023-05-10T20:00:00'
        end_time: '2023-05-10T20:01:00'
        timezone: 'IST'

    splunk:
        url: 'https://<<hostname>>'
        token: <<token>>
        search_query: 'index=_internal | fields _raw'
        start_time: '-1m'
        end_time: 'now'
   ```

4. Execute the script

* python siem-secret-finder.py

## References

* https://docs.splunk.com/Documentation/Splunk/9.0.4/RESTTUT/RESTsearches

* https://help.sumologic.com/docs/api/search-job/
