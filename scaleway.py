#!/bin/python3

import argparse
import os
import json
import shutil
import sys

class TScale:

    SCALEWAY_AUTH_KEYS = [
        ('SCW_ACCESS_KEY', 'https://console.scaleway.com/iam/api-keys'),
        ('SCW_SECRET_KEY', 'https://console.scaleway.com/iam/api-keys'),
        ('SCW_DEFAULT_ORGANIZATION_ID', 'https://console.scaleway.com/organization/settings'),
        ('SCW_DEFAULT_PROJECT_ID', 'https://console.scaleway.com/project/settings'),
    ]

    TERRAFORM_TEMPLATE = '''terraform {
    required_version = ">= 0.12.0"
    required_providers {
        scaleway = {
            source = "scaleway/scaleway"
        }
    }
}

provider "scaleway" {
    zone = "{{ZONE}}"
    region = "{{REGION}}"
}

resource "scaleway_instance_ip" "api" {

}

resource "scaleway_instance_server" "server" {
    type = "{{FLAVOR}}"
    image = "{{IMAGE}}"
    tags = {{TAGS}}
    name = "{{NAME}}"
    ip_id = scaleway_instance_ip.api.id
}

resource "scaleway_account_ssh_key" "key" {
    name = "user"
    public_key = "{{KEY_CONTENT}}"
}

resource "null_resource" "ansible" {
    triggers = {
        server_id = scaleway_instance_server.server.id
        playbook = md5(file("{{PLAYBOOK}}"))
    }

    provisioner "local-exec" {
        command = "ansible-playbook -i ${scaleway_instance_ip.api.address} {{PLAYBOOK}} --key-file ssh-key.pub"
    }
}
'''

    def __verbose_print(self, message):
        if self.args.verbose:
            print(message, file=sys.stderr, flush=True)

    def __check_env(self):
        for (key, url) in self.SCALEWAY_AUTH_KEYS:
            if not os.environ.get(key):
                raise Exception(f'Environment variable {key} is not set, please refer to {url}')

    def __args_as_dict(self):
        return self.args.__dict__

    def __parse_args(self):
        args = argparse.ArgumentParser(description='Create, delete or list VMs')
        args.add_argument('action',     help='Action to perform', choices=['create', 'delete', 'list'])

        args.add_argument('--name',     help='Name of the VM',                      required=True)

        args.add_argument('--image',    help='Image to use for the VM',             default='ubuntu_focal')
        args.add_argument('--flavor',   help='Flavor to use for the VM',            default='DEV1-S')

        args.add_argument('--tags',     help='Tags to use for the VM',              default=[], nargs='+')

        args.add_argument('--zone',     help='Zone to use for the VM',              default='fr-par-1')
        args.add_argument('--region',   help='Region to use for the VM',            default='fr-par')
        args.add_argument('--ssh-key',  help='SSH key to use for the VM',           default=os.path.expanduser('~/.ssh/id_rsa.pub'))
        args.add_argument('--playbook', help='Ansible playbook to use for the VM',  default='playbook.yml')
        args.add_argument('--overwrite',help='Overwrite existing VM',               default=False, type=bool)
        args.add_argument('--verbose',  help='Verbose mode',                        default=False, type=bool)

        self.args = args.parse_args()

        try:
            with open(self.args.ssh_key, 'r') as key:
                self.args.key_content = key.read().strip()
        except:
            self.__verbose_print(f'Warn: SSH Key {self.args.key} does not exist')
            self.args.key_content = None

        try:
            with open(self.args.playbook, 'r') as playbook:
                self.args.playbook_content = playbook.read()
        except:
            self.__verbose_print(f'Warn: Ansible playbook {self.args.playbook} does not exist')
            self.args.playbook_content = None

        self.args.tags = "[" + ", ".join(f'"{tag}"' for tag in self.args.tags) + "]"

        self.__verbose_print('Arguments parsed')
        self.__verbose_print(json.dumps(self.__args_as_dict(), indent=4))

    def __ensure_vms_folder(self):
        if not os.path.exists(self.vm_folders):
            self.__verbose_print(f'Creating folder {self.vm_folders}...')
            os.mkdir(self.vm_folders)

    def __list(self):
        if not os.path.exists(self.vm_folders):
            raise Exception(f'Folder {self.vm_folders} does not exist')
        return os.listdir(self.vm_folders)

    def __launch_terraform_cmds(self, cmds: list, dir_: str='.'):
        old_path = os.getcwd()

        self.__verbose_print(f'Changing directory to {dir_}...')
        os.chdir(dir_)

        for cmd in cmds:
            if os.system('terraform ' + cmd) != 0:
                raise Exception(f'Failed to run command {cmd}')

        self.__verbose_print(f'Changing directory back to {old_path}...')
        os.chdir(old_path)

    def __create(self):
        self.__ensure_vms_folder()
        if self.args.name in self.__list():
            if not self.args.overwrite:
                raise Exception(f'VM {self.args.name} already exists')
            else:
                print(f'VM {self.args.name} already exists, overwriting...')
                self.__delete()

        if not self.args.key_content:
            raise Exception(f'SSH Key does not exist')
        if not self.args.playbook_content:
            raise Exception(f'Ansible playbook does not exist')

        path = os.path.join(self.vm_folders, self.args.name)

        try:
            os.mkdir(path)
        except:
            raise Exception(f'Cannot create folder {path}')

        # Genrate main.tf
        template = self.TERRAFORM_TEMPLATE
        for k, v in self.__args_as_dict().items():
            if not isinstance(v, str):
                v = str(v).lower()
            template = template.replace('{{' + k.upper() + '}}', v)

        with open(os.path.join(path, 'main.tf'), 'w') as f:
            f.write(template)
        with open(os.path.join(path, 'playbook.yml'), 'w') as f:
            f.write(self.args.playbook_content)
        with open(os.path.join(path, 'ssh-key.pub'), 'w') as f:
            f.write(self.args.key_content)

        # Run terraform
        self.__launch_terraform_cmds([
            'init', 'apply -auto-approve', 'output -json > "output.json"'
        ], path)

        if self.args.verbose:
            print('VM created successfully')
            print('You can now connect to the VM using the following command:')
            try:
                with open(json_output, 'r') as json_output_data_file:
                    ip = json.load(json_output_data_file)['scaleway_instance_ip']['api']['address']
                    print(f'ssh -i {self.args.key} root@{ip}')
            except Exception as e:
                print('Failed to get VM IP because of the following error:')
                print(e)

    def __delete(self):
        self.__ensure_vms_folder()
        if self.args.name not in self.__list():
            raise Exception(f'VM {self.args.name} does not exist')

        path = os.path.join(self.vm_folders, self.args.name)

        try:
            # Run terraform
            self.__launch_terraform_cmds([
                'init', 'destroy -auto-approve'
            ], path)
        except e:
            self.__verbose_print("Failed to destroy scaleway instance (but no throw as program is using --overwrite=true)")
            if not self.args.overwrite:
                raise e

        os.rmdir(path)
        self.__verbose_print(f'VM {self.args.name} deleted successfully')

    def __init__(self, vm_folders='vms'):

        self.__parse_args()
        for binary in ('terraform', 'ansible-playbook'):
            if not shutil.which(binary):
                raise Exception(f'{binary} is not installed, please install it')
        self.vm_folders = vm_folders

    def run(self):
        if self.args.action == 'create':
            self.__check_env()
            self.__create()
        elif self.args.action == 'delete':
            self.__delete()
        elif self.args.action == 'list':
            print('\n'.join(self.__list()))

if __name__ == '__main__':
    try:
        TScale().run()
    except Exception as e:
        print(e)
        exit(1)
