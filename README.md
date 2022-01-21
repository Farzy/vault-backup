# vault-backup

Dump your Hashicorp Vault to a file. Not guaranteed to be consistent.
Dump is a form of commands to inject keys into Vault, so it is convenient to
use it later on to restore to different Vault, for example.

```bash
vault kv put /secret/users \
  test1_user='test_pass'
vault write /secret/dev/bash-org-244321 \
  AzureDiamond='hunter2'
```

# Environment variables

The following environment variables are used:
* `PYTHONIOENCODING` is used to ensure your keys are exported in valid encoding, make sure to use the same during import/export
* `VAULT_ADDR` - vault address endpoint to use, default is http://localhost:8200
* `VAULT_MOUNT` - Vault mount point to dump, optional, defaults to "secret"
* `TOP_VAULT_PREFIX` - path to dump, optional, useful when dumping only a fraction of the vault, defaults to "/"
* `VAULT_CACERT` - cert if using https:// with client cert, but actually not tested
* `VAULT_SKIP_VERIFY` - Skip TLS cert verification, default to false

# Known limitations

* Only KV Secrets Engine version 2 is supported.
* Delete items are ignored with a warning.
* You still need a Vault client in order to authenticate.
* You must have the right to list keys for `TOP_VAULT_PREFIX`, otherwise you will get an error with trace.

# Preparing Python environment

Under Ubuntu you need the following packages:

* python-pip
* python-virtualenv

```bash
virtualenv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Example usage

* Activate virtualenv.
* Export some vars:

```bash
export PYTHONIOENCODING=utf-8
export VAULT_ADDR=https://vault.tld:12345
export VAULT_MOUNT=it_secrets
export TOP_VAULT_PREFIX=/dev
```

* Authenticate to Vault, for example:

```bash
vault auth -method=ldap username=your-username
```

* After successful authorization you can run dump script and encrypt it with GPG to the output file:

```bash
python vault-dump.py | gpg -e -r GPG_KEY_ID > vault.dump.txt.gpg
```

# Importing to new vault

**Warning**: All corresponding keys will be overwritten.

* Authenticate to Vault, for example:

```bash
vault auth -method=ldap username=user-in-new-vault
```

* Disable bash history, decrypt encrypted file and execute commands stored inside:

```bash
set +o history
. <(gpg -qd vault.dump.txt.gpg)
```
