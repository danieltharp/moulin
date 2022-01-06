import validator
import os

def run(job_name, verbose=True, dryrun=False):
    if verbose is True: print(f'Validating {job_name} job prior to run...')
    job = validator.parse_job(job_name)
    if verbose is True: print(f'Validated {job_name}...')
    if verbose is True: print(f'Constructing AWS API call')
    # `aws s3 sync `
    cmd = "aws s3 sync --size-only "
    # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket`
    cmd += '"' + job['path'] + '" "s3://' + job['bucket']
    if job['prefix'][0] != '/':
        # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/`
        cmd += '/'
    # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts`
    cmd += job['prefix']
    if job['prefix'][-1] != '/':
        # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/`
        cmd += '/'
    cmd += '"'
    if job['first_filter'] == 'include':
        for inc in job['include']:
            # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --include "*.py" --include "*.sh`
            cmd += ' --include "' + inc + '"'
        if job['exclude']:
            for exc in job['exclude']:
                # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --include "*.py" --include "*.sh" --exclude "scratch.py"`
                cmd += ' --exclude "' + exc + '"'
    else:
        for exc in job['exclude']:
            # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --exclude "*"`
            cmd += ' --exclude "' + exc + '"'
        for inc in job['include']:
            # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --exclude "*" --include "*.py" --include "*.sh"`
            cmd += ' --include "' + inc + '"'
    # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --exclude "*" --include "*.py" --include "*.sh" --storage-class STANDARD_IA`
    cmd += ' --storage-class ' + job['storage_class']
    if job['remove_missing_files'] is True:
        # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --exclude "*" --include "*.py" --include "*.sh" --storage-class STANDARD_IA --delete true`
        cmd += ' --delete true'
    if dryrun:
        # `aws s3 sync /home/bluesoul/scripts s3://my-s3-bucket/scripts/ --exclude "*" --include "*.py" --include "*.sh" --storage-class STANDARD_IA --delete true --dry-run`
        cmd += ' --dryrun'
    print(cmd)
    os.system(cmd)
    print('Complete!')
