import toml
from cron_validator import CronScheduler

def parse(verbose=False):
    if verbose is True: print("retrieving configuration...")
    with open('conf/schedules.toml', 'r') as f:
        schedule_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/schedules.toml to TOML parser...')
    with open('conf/backups.toml', 'r') as f:
        backups_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/backups.toml to TOML parser...')
    with open('conf/config.toml', 'r') as f:
        config_toml = toml.load(f)
        if verbose is True: print('Successfully passed conf/config.toml to TOML parser...')
    if verbose is True: print('Determining default schedule...')
    if 'default_interval' not in config_toml['main']:
        if verbose is True: print('The default_interval key is missing from config.toml [main], finding the first item in conf/schedules.toml.')
        default_interval = list(schedule_toml['schedule'].keys())[0]
        default_expr = schedule_toml['schedule'][default_interval]['expr']
    else:
        default_interval = config_toml['main']['default_interval']
        default_expr = schedule_toml['schedule'][default_interval]['expr']
    if verbose is True: print(f'Default interval: {default_interval} ({default_expr})')

    for backup in backups_toml['backups'].keys():
        interval = backups_toml['backups'][backup].get('schedule', default_interval)
        next_run = CronScheduler(schedule_toml['schedule'][interval]['expr'])
        if verbose is True: print(f'Backup job {backup} next run: {str(next_run.next_execution_time)} ({interval})')

