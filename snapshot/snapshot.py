#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argparse
import os
import re
import datetime

#from keystoneclient.auth.identity import v2
#from keystoneclient import session
from novaclient.client import Client
from cinderclient.v1 import client as clientcinder

# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.CRITICAL)
#LOG.setLevel(logging.INFO)

INSECURE=True

#Retention image
IMAGE_RET=2

#Retention volume
VOLUME_RET=2

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
PARSER.add_argument("-l", "--list",
            action='store_true',
            help="print snapshot",
            default=False)
PARSER.add_argument("-c", "--clean",
            action='store_true',
            help="clean snapshot",
            default=False)
PARSER.add_argument("-s", "--snapshot",
            action='store_true',
            help="Start snapshot",
            default=False)
PARSER.add_argument("-t", "--type",
            help="type of snapshot (ex : image|volume|all)")
PARSER.add_argument("-i", "--id",
            help="type of snapshot (ex : <id_image>|<id_volume>|all)")
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
                  os_auth_url,
                  insecure=INSECURE)

    self.cinder = clientcinder.Client(os_username,
                                      os_password,
                                      os_tenant_name,
                                      os_auth_url,
                                      service_type="volume")

  def get_snapshot_list(self,type):
      "print snapshot"
      LOG.info('Start list snapshot ...')
      print "Snapshot Images : "
      for image in self.nova.images.list():
        if image.name.startswith('backup'):
          print "%s" % (image.name)

      #print self.nova.volumes.list()
      #print self.nova.volume_snapshots.list()
      #print self.cinder.volumes.list()


      print "Snapshot Volumes : "
      for volume in self.cinder.volume_snapshots.list():
        #help(volume)
        print "%s %s" % (volume.id, volume.display_name)

  def clean_snapshot(self,id):
      "clean snapshot"
      LOG.info('Start clean snapshot ...')
      startname='backup_'+id
      for volume in self.cinder.volume_snapshots.list():
        if image.name.startswith(startname):
          #help(volume)
          print "%s %s" % (volume.id, volume.display_name)

  def snapshot(self,type,id):
      "Start snapshot"
      LOG.info('Start snapshot ...')
      if type == 'image':
          self.snap_image(id)
      elif type == 'volume':
          self.snap_volume(id)
      elif type == 'all':
          self.snap_image('all')
          self.snap_volume('all')
      else:
          print "Error param type"

  def snap_image(self,id):
      "Start image snapshot"
      LOG.info('Start snapshot image ...')
      if id == 'all':
        for server in self.nova.servers.list():
          print "start snap image %s" % (server.name)
          snapname = 'backup_' +server.name+'_'+datetime.datetime.now().strftime('%Y%m%d')
          self.nova.servers.get(id).backup(snapname, 'daily', IMAGE_RET)
      else:
        print "start snapshot image %s" % id
        snapname = 'backup_' +self.nova.servers.get(id).name+'_'+datetime.datetime.now().strftime('%Y%m%d')
        self.nova.servers.get(id).backup(snapname, 'daily', IMAGE_RET)


  def snap_volume(self,id):
      "Start volume snapshot"
      LOG.info('Start volume snapshot ...')
      if id == 'all':
        for volume in self.cinder.volumes.list():
          print "start snap image %s" % (volume.id)
          snapname = 'backup_' +volume.id+'_'+datetime.datetime.now().strftime('%Y%m%d')
          print snapname
          #self.nova.servers.get(id).backup(snapname, 'daily', IMAGE_RET)
      else:
        print "start snapshot image %s" % id
        snapname = 'backup_' +self.cinder.volumes.get(id).id+'_'+datetime.datetime.now().strftime('%Y%m%d')
        #self.nova.servers.get(id).backup(snapname, 'daily', VOLUME_RET)

#  def export_vms_configs(self,export_all):
#      "export vms configurations like flavors, names, sshkey ..."
#      LOG.info('Start export configs ...')
#      print ("Export in %s" % export_all)
#      for server in self.nova.servers.list():
#        name        = server.name
#        flavor      = self.nova.flavors.get(server.flavor['id']).name
#        image       = self.nova.images.get(server.image['id']).name
#        security    = (', '.join(str(x['name']) for x in server.security_groups))
#        keyname     = server.key_name
#        addresses   = ''
#        for inter in server.addresses.values():
#            for subnet in inter:
#                addresses += ' '+subnet.get('addr')
#        #addresses   = ', '.join([inter[0].get('addr') for inter in server.addresses.values()])
#        print "|%s| |%s| |%s| |%s| |%s| |%s|" % (name,
#                                       flavor,
#                                       image,
#                                       security,
#                                       keyname,
#                                       addresses,
#        )

if __name__ == "__main__":

   novamanage = NovaManage(nova_version=ARGS.nova_version,
                           os_username=ARGS.os_username,
                           os_password=ARGS.os_password,
                           os_tenant_name=ARGS.os_tenant_name,
                           os_auth_url=ARGS.os_auth_url)

   # List snapshot
   if ARGS.list:
       arg_type = ARGS.type
       if ARGS.type:
           arg_type = ARGS.type
       else:
           arg_type = 'all'

       novamanage.get_snapshot_list(type=arg_type)
   # Clean snapshot
   elif ARGS.clean:
       novamanage.clean_snapshot(type=ARGS.type)
   # Export conf
   elif ARGS.snapshot:
       novamanage.snapshot(type=ARGS.type,id=ARGS.id)
   else:
       PARSER.print_help()
