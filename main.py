import argparse
import toml
import cron_validator
import boto3
import validator
import scheduler
import runner

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--validate", help="validate your config files", action="store_true")
parser.add_argument("-t", "--times", help="check the next runtime for each backup job", action="store_true")
parser.add_argument("-r", "--run", help="run the specified backup job now, ignoring its schedule", action="store")
parser.add_argument("-s", "--scheduled", help="check for any jobs that need to run and run them", action="store_true")
args = parser.parse_args()
if args.validate:
    validator.validate_configs(verbose=True)
if args.times:
    scheduler.parse(verbose=True)
if args.run:
    runner.run(job_name=args.run)
