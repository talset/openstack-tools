#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argparse
import os
#from keystoneclient.auth.identity import v2
#from keystoneclient import session
from novaclient.client import Client

# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.CRITICAL)
LOG.setLevel(logging.INFO)

# Get args
PARSER = argparse.ArgumentParser()
PARSER.add_argument("-osti", "--os-tenant-id",
            help="Tenant to request authorization on. Defaults to env[OS_TENANT_ID]",
            default=os.getenv('OS_TENANT_ID'))
PARSER.add_argument("-ostn", "--os-tenant-name",
            help="Tenant to request authorization on. Defaults to env[OS_TENANT_NAME]",
            default=os.getenv('OS_TENANT_NAME'))
PARSER.add_argument("-osu", "--os-username",
            help="Name used for authentication with the OpenStack Identity service. Defaults to env[OS_USERNAME]",
            default=os.getenv('OS_USERNAME'))
PARSER.add_argument("-osp", "--os-password",
            help="Password used for authentication with the OpenStack Identity service. Defaults to env[OS_PASSWORD]",
            default=os.getenv('OS_PASSWORD'))
PARSER.add_argument("-osurl", "--os-auth-url",
            help="Specify the Identity endpoint to use for authentication. Defaults to env[OS_AUTH_URL]",
            default=os.getenv('OS_AUTH_URL'))
PARSER.add_argument("-nv", "--nova-version",
            help="Nova client version. Defaults to 2",
            default=2)
PARSER.add_argument("-f", "--floatingip",
            help="Floating to attach. Default to 84.39.36.21",
            default="84.39.36.21")
PARSER.add_argument("-i", "--instance",
            help="Instance id or name to attach. Default to lb1",
            default="lb1")
ARGS = PARSER.parse_args()


class NovaManage(object):

  def __init__(self, nova_version, os_username, os_password, os_tenant_name, os_auth_url):
    logformat =  '%(asctime)s %(levelname)s -: %(message)s'
    # Set logger formater
    formatter = logging.Formatter(logformat)
    hdl = logging.StreamHandler(); hdl.setFormatter(formatter); LOG.addHandler(hdl)

    print "%s %s %s %s %s" % (nova_version, os_username, os_password, os_tenant_name, os_auth_url)
    self.nova = Client(nova_version,
                  os_username,
                  os_password,
                  os_tenant_name,
                  os_auth_url)

  def add_floating(self,instance,floating):
      "attach floating ip to instance"
      LOG.info('Start attach configs ...')

      self.nova.servers.add_floating_ip(server=instance,address=floating)

if __name__ == "__main__":

   novamanage = NovaManage(nova_version=ARGS.nova_version,
                           os_username=ARGS.os_username,
                           os_password=ARGS.os_password,
                           os_tenant_name=ARGS.os_tenant_name,
                           os_auth_url=ARGS.os_auth_url)

   # Export conf
   if ARGS.instance:
       novamanage.add_floating(instance=ARGS.instance, floating=ARGS.floatingip)
   else:
       PARSER.print_help()
