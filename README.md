# Scaleway-Deployer

Deploy scaleway instances using ansible and terraform

```
usage: scaleway.py [-h] --name NAME [--image IMAGE] [--flavor FLAVOR]
                   [--tags TAGS [TAGS ...]] [--zone ZONE] [--region REGION]
                   [--ssh-key SSH_KEY] [--login LOGIN] [--playbook PLAYBOOK]
                   [--overwrite OVERWRITE] [--verbose VERBOSE]
                   {create,delete,list}

Create, delete or list VMs

positional arguments:
  {create,delete,list}  Action to perform

options:
  -h, --help            show this help message and exit
  --name NAME           Name of the VM
  --image IMAGE         Image to use for the VM
  --flavor FLAVOR       Flavor to use for the VM
  --tags TAGS [TAGS ...]
                        Tags to use for the VM
  --zone ZONE           Zone to use for the VM
  --region REGION       Region to use for the VM
  --ssh-key SSH_KEY     SSH key to use for the VM
  --playbook PLAYBOOK   Ansible playbook to use for the VM
  --overwrite OVERWRITE
                        Overwrite existing VM
  --verbose VERBOSE     Verbose mode
```

## Requirements:
- python3
- ansible
- terraform

Thoses environments variables must be set:
```
export SCW_ACCESS_KEY='xxx' # https://console.scaleway.com/iam/api-keys
export SCW_SECRET_KEY='xxx' # https://console.scaleway.com/iam/api-keys
export SCW_DEFAULT_ORGANIZATION_ID='xxx' # https://console.scaleway.com/organization/settings
export SCW_DEFAULT_PROJECT_ID='xxx' # https://console.scaleway.com/project/settings
```

## Example:

Basic create:
```bash
python3 scaleway.py create --name "test"
```
Deploys an instance with:
    - name: `test`
    - image: `ubuntu_focal`
    - flavor: `DEV1-S`
    - tags: `[]`
    - zone: `fr-par-1`  
    - region: `fr-par`
    - ssh-key: `~/.ssh/id_rsa.pub`
    - playbook: `playbook.yml`
    - overwrite: `False`
    - verbose: `False`
