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
PARSER.add_argument("-t", "--tenant",
            help="Which tenant to list floating ips. Defaults to env[OS_TENANT_NAME]",
            default=os.getenv('OS_TENANT_NAME'))
PARSER.add_argument("-f", "--flavors",
            action='store_true',
            help="print flavor for each vms",
            default=False)
ARGS = PARSER.parse_args()


class FloatingUsage(object):

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

  def get_all_vm_flavors(self):
      "print flavors for each vm in the tenant"
      LOG.info('Start list flavors vms ...')
      for server in self.nova.servers.list():
        print "%s %s" % (server.name, self.nova.flavors.get(server.flavor['id']).name)
 
  def export_vms_configs(self,export_all):
      "export vms configurations like flavors, names, sshkey ..."
      LOG.info('Start export configs ...')
      print ("Export in %s" % export_all)
      for server in self.nova.servers.list():
        name        = server.name
        flavor      = self.nova.flavors.get(server.flavor['id']).name
        image       = self.nova.images.get(server.image['id']).name
        security    = (', '.join(str(x['name']) for x in server.security_groups))
        keyname     = server.key_name
        addresses   = ''
        for inter in server.addresses.values():
            for subnet in inter:
                addresses += ' '+subnet.get('addr')
        #addresses   = ', '.join([inter[0].get('addr') for inter in server.addresses.values()])
        print "|%s| |%s| |%s| |%s| |%s| |%s|" % (name,
                                       flavor,
                                       image,
                                       security,
                                       keyname,
                                       addresses,
        )

if __name__ == "__main__":

   floatingusage = FloatingUsage(nova_version=ARGS.nova_version,
                           os_username=ARGS.os_username,
                           os_password=ARGS.os_password,
                           os_tenant_name=ARGS.os_tenant_name,
                           os_auth_url=ARGS.os_auth_url)

   # List flavors
   if ARGS.flavors:
       floatingusage.get_all_vm_flavors()
   # Export conf
   elif ARGS.export_all:
       floatingusage.export_vms_configs(export_all=ARGS.export_all)
   else:
       PARSER.print_help()
