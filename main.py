import argparse
import toml
import cron_validator
import boto3
import validator

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--validate", help="validate your config files",
                    action="store_true")
args = parser.parse_args()
if args.validate:
    validator.validate(verbose=True)