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
