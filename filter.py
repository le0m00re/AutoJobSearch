import datetime
import pandas as pd
import parse_settings

def print_message(message, outlog):
    print(f"[MESSAGE] {message}", file=outlog)
def print_fail(fail, outlog):
    print(f"[FATAL ERROR] {fail}", file=outlog)
def print_success(success, outlog):
    print(f"[SUCCESS] {success}", file=outlog)

def filter(unfiltered_jobs, timestart_prefix, whitelist_filepath, 
blacklist_filepath, outlog, url_csv):
    start = datetime.datetime.now()

    try:
        companies, locations = url_csv[['company', 'city']].T.values
        locations_whitelist = pd.unique(locations)
        locations_whitelist = list(locations_whitelist)
        # locations_whitelist.extend(['Location', 'Remote'])
        locations_whitelist.extend([term[1:].strip() for term \
            in titles_whitelist if term[0] == '@'])
        
        with open(whitelist_filepath, encoding='utf-8') as f:
            titles_whitelist = [line.strip() for line in f.readlines()]
        with open(blacklist_filepath, encoding='utf-8') as f:
            titles_blacklist = [line.strip() for line in f.readlines()]
        locations_blacklist = [term[1:].strip for term \
            in titles_blacklist if term[0] == '@']

        filtered_dict = {'company': [],
                'title': [],
                'location': [],
                'postdate': [],
                'jobpage': [],
                'location_status': [],
                'title_status': []}

        for i, opening in unfiltered_jobs.iterrows():
            if isinstance(opening['title'], float):
                continue
            opening_on_whitelist = any(title in opening['title'] for title \
                in titles_whitelist)
            opening_on_blacklist = any(title in opening['title'] for title \
                in titles_blacklist)
            if (isinstance(opening['location'], float) 
            or ('<' in opening['location'] and '>' in opening['location'])):
                opening_in_location == True
                # print(opening['location'], ' is a float')
            else:
                opening_in_location = any(location in opening['location'] 
                    for location in locations_whitelist) and \
                    not any(location in opening['location'] 
                    for location in locations_blacklist)

            # if (opening_in_location 
            # and (opening_on_whitelist or not opening_on_blacklist)):
            filtered_dict['company'].extend([opening['company']])
            filtered_dict['title'].extend([opening['title']])
            filtered_dict['location'].extend([opening['location']])
            filtered_dict['postdate'].extend([opening['postdate']])
            filtered_dict['jobpage'].extend([opening['jobpage']])
            if not opening_in_location:
                filtered_dict['location_status'].append('location blacklisted')
            else:
                filtered_dict['location_status'].append('location whitelisted')
            if opening_on_whitelist:
                filtered_dict['title_status'].append('whitelist explicit')
            elif opening_on_blacklist:
                filtered_dict['title_status'].append('blacklist')
            else:
                filtered_dict['title_status'].append('whitelist implicit')
    
        df = pd.DataFrame(filtered_dict)
        df.to_csv(f"output\\manual_{timestart_prefix}_jobs_filtered.csv", mode='a', 
            index=False, header=True)
        print_success('Filter finished normally.', outlog)
    except Exception as e:
        print_fail(f"Filter failed due to {type(e)}", outlog)
        raise e
    finally:
        end = datetime.datetime.now()
        print_message(f"Filter ran "\
            f"for {(end-start).total_seconds()/60} minutes", outlog)

if __name__ == '__main__':
    start = datetime.datetime.now()
    timestart_prefix = start.strftime("%y-%m-%d_%H-%M-%S")
    outlog = open(f'output\\manual_{timestart_prefix}_filter.log', 'a', 
        encoding='utf-8')
    settings = parse_settings.parse_settings()
    try:
        unfiltered_jobs = pd.read_csv(settings['UNFILTERED_JOBS_CSV'])
        url_csv = pd.read_csv(settings['URL_CSV'])
        filter(unfiltered_jobs, timestart_prefix, settings['TITLE_WHITELIST'],
            settings['TITLE_BLACKLIST'], outlog, url_csv)
    except FileNotFoundError as e:
        print_fail(f"The file {settings['UNFILTERED_JOBS_CSV']} "\
            "does not exist.")
    finally:
        outlog.close()