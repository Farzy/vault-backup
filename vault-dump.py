#! /usr/bin/env python3
#
# Dumps a HashiCorp Vault KV v2 database to write statements.
# Useful for backing up in-memory vault data
# and later restoring from the generated script.
#
# Requires: an already-authenticated session
#
# Reads env vars:
# - VAULT_ADDR  which points to desired Hashicorp Vault instance, default http://localhost:8200
# - VAULT_MOUNT to specify the mount point to dump, default 'secret'
# - TOP_VAULT_PREFIX to specify path to dump, for partial backups, default /secret/
#
# Use custom encoding:
#   PYTHONIOENCODING=utf-8 python vault-dump.py
#
# Copyright (c) 2017 Shane Ramey <shane.ramey@gmail.com>
# Licensed under the Apache License, Version 2.0
from __future__ import print_function
import sys
import subprocess
import os
import pwd
import hvac
import datetime


def print_header():
    user = pwd.getpwuid(os.getuid()).pw_name
    date = "{} UTC".format(datetime.datetime.utcnow())

    print ('#')
    print ('# vault-dump.py backup')
    print ("# dump made by {}".format(user))
    print ("# backup date: {}".format(date))
    print ("# VAULT_ADDR env variable: {}".format(hvac_url))
    print ("# VAULT_MOUNT env variable: {}".format(vault_mount))
    print ("# TOP_VAULT_PREFIX env variable: {}".format(top_vault_prefix))
    print ('# STDIN encoding: {}'.format(sys.stdin.encoding))
    print ('# STDOUT encoding: {}'.format(sys.stdout.encoding))
    print ('#')
    print ('# WARNING: not guaranteed to be consistent!')
    print ('#')


# looks at an argument for a value and prints the key
#  if a value exists
def recurse_for_values(mount, path):
    entries = client.secrets.kv.v2.list_secrets(mount_point=vault_mount, path=path)
    candidate_values = entries['data']['keys']
    for candidate_value in candidate_values:
        if candidate_value.endswith('/'):
            recurse_for_values(mount, path + candidate_value)
        else:
            item_path = path + candidate_value
            try:
                final_data = client.secrets.kv.v2.read_secret(mount_point=mount, path=item_path)
            except hvac.exceptions.InvalidPath: # Exception raised if item is deleted
                final_data = {}
            if 'data' in final_data:
                final_dict = final_data['data']['data']
                print("vault kv put {}{}".format(vault_mount, item_path), end='')

                sorted_final_keys = sorted(final_dict.keys())
                for final_key in sorted_final_keys:
                    final_value = final_dict[final_key]
                    print(" '{0}'={1}".format(final_key, repr(final_value)), end='')
                print()
            else:
                print("# WARNING: {} is deleted".format(repr(item_path)))


env_vars = os.environ.copy()
hvac_token = subprocess.check_output(
    "vault read -field id auth/token/lookup-self",
    shell=True,
    env=env_vars)

hvac_url = os.environ.get('VAULT_ADDR','http://localhost:8200')
hvac_client = {
    'url': hvac_url,
    'token': hvac_token,
}
client = hvac.Client(**hvac_client)
if os.environ.get('VAULT_SKIP_VERIFY'):
    import requests
    rs = requests.Session()
    client.session = rs
    rs.verify = False
    import warnings
    warnings.filterwarnings("ignore")
assert client.is_authenticated()

vault_mount = os.environ.get('VAULT_MOUNT', 'secret')
top_vault_prefix = os.environ.get('TOP_VAULT_PREFIX','/')

print_header()
recurse_for_values(vault_mount, top_vault_prefix + "/")
