from os import path

from cron_validator import CronValidator
import toml
import re

def validate_configs(verbose=False):
    print("Validating config...")

    if verbose is True: print("Checking for existence of all required files...")
    schedules_exist = path.exists('conf/schedules.toml')
    main_config_exists = path.exists('conf/config.toml')
    backup_config_exists = path.exists('conf/backups.toml')
    if schedules_exist and main_config_exists and backup_config_exists:
        if verbose is True: print('All required config files were found...')
    else:
        if not schedules_exist:
            raise FileNotFoundError('Did not find conf/schedules.toml')
        if not main_config_exists:
            raise FileNotFoundError('Did not find conf/config.toml')
        if not backup_config_exists:
            raise FileNotFoundError('Did not find conf/backups.toml')

    if verbose is True: print('Inspecting conf/schedules.toml...')
    with open('conf/schedules.toml', 'r') as f:
        schedule_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/schedules.toml to TOML parser...')
    if not 'schedule' in schedule_toml:
        raise IndexError('At least one [schedule] block must be defined in conf/schedules.conf!')
    if verbose is True: print(f'Found {str(len(schedule_toml["schedule"]))} schedule items...')
    toml_safe_name = re.compile("^[a-zA-Z0-9_-]*$")
    schedule_names = list(schedule_toml['schedule'].keys())
    for schedule in schedule_toml['schedule']:
        if verbose is True: print(f'Processing {schedule} name field...')
        if toml_safe_name.match(schedule) is None:
            raise ValueError('Invalid name. Valid values: Uppercase and lowercase letters, numbers, dash, underscore.')
        if verbose is True: print(f'Processing {schedule} cron expression...')
        if CronValidator.parse(schedule_toml['schedule'][schedule]['expr']) is None:
            raise ValueError('Invalid cron syntax.')
    if verbose is True: print('Schedule file is valid!')

    if verbose is True: print('Inspecting conf/config.toml...')
    with open('conf/config.toml', 'r') as f:
        config_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/config.toml to TOML parser...')
    if 'main' not in config_toml:
        raise KeyError('The [main] block is missing from conf/config.toml!')
    if verbose is True: print('Parsing [main] values...')
    if 'remove_missing_files' not in config_toml['main']:
        print('Notice: The remove_missing_files key is missing from config.toml [main], assuming false.')
    else:
        if type(config_toml['main']['remove_missing_files']) != bool:
            raise ValueError('remove_missing_files should be true or false')
    if 'default_interval' not in config_toml['main']:
        print('Warning: The default_interval key is missing from config.toml [main], assuming the first item in conf/schedules.toml.')
    else:
        if config_toml['main']['default_interval'] not in schedule_names:
            raise ValueError('default_interval value in config.toml does not match a schedule name in schedules.toml')
    if 'aws' not in config_toml:
        raise KeyError('The [aws] block is missing from conf/config.toml!')
    if verbose is True: print('Parsing [aws] values...')
    if 'region' not in config_toml['aws']:
        raise KeyError('A region must be set under [aws] in config.toml, e.g., region = "us-east-1"')
    if type(config_toml['aws']['region']) != str:
        raise ValueError('The region under [aws] in config.toml must be a string, e.g., region = "us-east-1"')
    if 'storage_class' not in config_toml['aws']:
        raise KeyError('A storage_class must be set under [aws] in config.toml, e.g., storage_class = "GLACIER"')
    if type(config_toml['aws']['storage_class']) != str:
        raise ValueError('The storage_class under [aws] in config.toml must be a string, e.g., storage_class = "GLACIER"')
    if config_toml['aws']['storage_class'] not in ['STANDARD','REDUCED_REDUNDANCY','STANDARD_IA','ONEZONE_IA',
                                                   'INTELLIGENT_TIERING','GLACIER','DEEP_ARCHIVE','GLACIER_IR']:
        raise ValueError(
            "The storage_class under [aws] in config.toml must be one of 'STANDARD','REDUCED_REDUNDANCY','STANDARD_IA','ONEZONE_IA',"
            "'INTELLIGENT_TIERING','GLACIER','DEEP_ARCHIVE','GLACIER_IR'")
    if 'bucket' not in config_toml['aws']:
        raise KeyError('A bucket must be set under [aws] in config.toml, e.g., bucket = "my-s3-bucket"')
    if type(config_toml['aws']['bucket']) != str:
        raise ValueError('The bucket under [aws] in config.toml must be a string, e.g., bucket = "my-s3-bucket"')
    if 'prefix' not in config_toml['aws']:
        print('Notice: The prefix key is missing from config.toml [aws], assuming bucket root.')
    else:
        if type(config_toml['aws']['prefix']) != str:
            raise ValueError('The prefix under [aws] in config.toml must be a string, e.g., prefix = "/path/to/backups"')
    if verbose is True: print('Config file is valid!')

    if verbose is True: print('Inspecting conf/backups.toml...')
    with open('conf/backups.toml', 'r') as f:
        backups_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/backups.toml to TOML parser...')
    if 'backups' not in backups_toml:
        raise KeyError('No [backups] block was found in conf/backups.toml!')
    if len(backups_toml['backups']) == 0:
        raise ValueError('A [backups] block was found but no backups were defined in conf/backups.toml!')
    alphanum = re.compile("^[a-z0-9]*$")
    for key in list(backups_toml['backups'].keys()):
        if verbose is True: print(f'Parsing [backups.{key}]...')
        if alphanum.match(key) is None:
            raise KeyError(f'A backup definition name may only use lowercase letters and numbers, e.g., [backups.documents], {key} is invalid.')
        if 'path' not in backups_toml['backups'][key]:
            raise KeyError(f'[backups.{key}] is missing a path definition!')
        if not path.exists(backups_toml['backups'][key]['path']):
            raise ValueError(f'[backups.{key}] path does not exist!')
        if 'schedule' in backups_toml['backups'][key]:
            if backups_toml['backups'][key]['schedule'] not in schedule_names:
                raise ValueError(f'[backups.{key}] schedule does not exist in conf/schedules.toml!')
        if 'storage_class' in backups_toml['backups'][key]:
            if backups_toml['backups'][key]['storage_class'] not in ['STANDARD','REDUCED_REDUNDANCY','STANDARD_IA',
                                                                'ONEZONE_IA','INTELLIGENT_TIERING','GLACIER',
                                                                'DEEP_ARCHIVE','GLACIER_IR']:
                raise ValueError(
                    f"The storage_class under [backups.{key}] in backups.toml must be one of 'STANDARD','REDUCED_REDUNDANCY','STANDARD_IA','ONEZONE_IA',"
                    "'INTELLIGENT_TIERING','GLACIER','DEEP_ARCHIVE','GLACIER_IR'"
                    )
        if 'exclude' in backups_toml['backups'][key]:
            if isinstance(backups_toml['backups'][key]['exclude'], list) == False or all(isinstance(elem, str) for elem in backups_toml['backups'][key]['exclude']) == False:
                raise ValueError(f'The exclude statement for [backups.{key}] should be a list of strings representing files or folders beneath the path.')
        if 'include' in backups_toml['backups'][key]:
            if isinstance(backups_toml['backups'][key]['include'], list) == False or all(isinstance(elem, str) for elem in backups_toml['backups'][key]['include']) == False:
                raise ValueError(f'The include statement for [backups.{key}] should be a list of strings representing files or folders beneath the path.')
        if 'exclude' in backups_toml['backups'][key] and 'include' in backups_toml['backups'][key]:
            keys_in_order = list(backups_toml['backups'][key].keys())
            if keys_in_order.index('include') < keys_in_order.index('exclude') and backups_toml['backups'][key]['exclude'] == ['*']:
                print(f'Warning: [backup.{key}] will not back up any files due to exclude = ["*"] coming after the include statement.')
            if keys_in_order.index('include') > keys_in_order.index('exclude') and backups_toml['backups'][key]['include'] == ['*']:
                print(f'Notice: [backup.{key}] will back up all files due to include = ["*"] coming after the exclude statement.')
        if 'prefix' in backups_toml['backups'][key]:
            if type(backups_toml['backups'][key]['prefix']) != str:
                raise ValueError(f'The prefix statement for [backups.{key}] must be a string.')
        if 'bucket' in backups_toml['backups'][key]:
            if type(backups_toml['backups'][key]['bucket']) != str:
                raise ValueError(f'The bucket statement for [backups.{key}] must be a string.')
        if 'region' in backups_toml['backups'][key]:
            if type(backups_toml['backups'][key]['region']) != str:
                raise ValueError(f'The region statement for [backups.{key}] must be a string.')
        if 'remove_missing_files' in backups_toml['backups'][key]:
            if type(backups_toml['backups'][key]['remove_missing_files']) != bool:
                raise ValueError(f'The remove_missing_files statement for [backups.{key}] must be a bool.')
    if verbose is True: print("Backups file is valid!")
    print("All files are valid!")

def parse_job(job_name, verbose=True):
    job = {}
    # We need to know a number of things to feed to AWS: bucket, prefix, region, path, remove_missing_files, storage_class, include, and exclude.
    with open('conf/backups.toml', 'r') as f:
        backups_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/backups.toml to TOML parser...')
    with open('conf/config.toml', 'r') as f:
        config_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/config.toml to TOML parser...')
    job['region'] = backups_toml['backups'][job_name].get('region', config_toml['aws']['region'])
    job['bucket'] = backups_toml['backups'][job_name].get('bucket', config_toml['aws']['bucket'])
    job['prefix'] = backups_toml['backups'][job_name].get('prefix', config_toml['aws'].get('prefix', '/'))
    job['storage_class'] = backups_toml['backups'][job_name].get('storage_class', config_toml['aws']['storage_class'])
    job['remove_missing_files'] = backups_toml['backups'][job_name].get('remove_missing_files', config_toml['aws'].get('remove_missing_files', False))
    job['path'] = backups_toml['backups'][job_name]['path']
    job['include'] = backups_toml['backups'][job_name].get('include', None)
    job['exclude'] = backups_toml['backups'][job_name].get('exclude', None)
    # We also need to know the order of include vs. exclude
    # Neither one being present is the same as include *, exclude none.
    if job['include'] is None and job['exclude'] is None:
        job['first_filter'] = 'include'
        job['include'] = ['*']
    # A missing exclude statement should be handled as exclude *, include the contents of the var
    elif job['include'] is not None and job['exclude'] is None:
        job['first_filter'] = 'exclude'
        job['exclude'] = ['*']
    # A missing include statement should be the inverse, include * and exclude the contents of the var
    elif job['exclude'] is not None and job['include'] is None:
        job['first_filter'] = 'include'
        job['include'] = ['*']
    # Finally, both being present means we need to follow the order specified in the TOML file.
    # Thankfully, updates to python 3 preserve the order of dicts when loaded by the toml library.
    else:
        if list(backups_toml['backups'][job_name]).index('include') < list(backups_toml['backups'][job_name]).index('exclude'):
            job['first_filter'] = 'include'
        else:
            job['first_filter'] = 'exclude'
    return job
