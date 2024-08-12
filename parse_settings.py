def parse_settings():
    '''Imports settings from settings.ini and turns it into dict'''
    with open('settings.ini', 'r') as f:
        ini = [line.strip() for line in f.readlines() if line[0] not in (';', '[')]
        ini_filtered = list(filter(None, ini))
        settings_dict = {k:v for (k,v) in [setting.split('=') for setting in ini_filtered]}
        settings_dict['SLEEP'] = float(settings_dict['SLEEP'])
        return settings_dict


