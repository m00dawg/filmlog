#!/bin/bash
cd ansible
ansible-playbook deploy.yml -i inventory
cd ..
