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
from cinderclient import client as clientcinder

# Init logging level with debug stream handler
LOG = logging.getLogger()
LOG.setLevel(logging.CRITICAL)
#LOG.setLevel(logging.INFO)

INSECURE=True

#Retention image
IMAGE_RET=7

#Retention volume
VOLUME_RET=7

#Retention VFS Volume from snapshot
VOLUMEFROMSNAP_RET=1

DEBUG=False

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
PARSER.add_argument("-vfs", "--volumefromsnap",
            action='store_true',
            help="Create a volume from the last volume_snapshot (--id need to be a volume_snapshot id",
            default=False)
PARSER.add_argument("-t", "--type",
            help="type of snapshot (ex : image|volume|all)")
PARSER.add_argument("-i", "--id",
            help="id to backup (ex : <id_image>|<id_volume>|all)")
ARGS = PARSER.parse_args()


class BackupManage(object):

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
                  insecure=True)

    self.cinder = clientcinder.Client(nova_version,
                                      os_username,
                                      os_password,
                                      os_tenant_name,
                                      os_auth_url,
                                      service_type="volume",
                                      insecure=INSECURE)

    self.cinder.authenticate()
    self.cinder_endpoint_version=self.cinder.get_volume_api_version_from_endpoint()
    self.cinder = clientcinder.Client(self.cinder_endpoint_version,
                                      os_username,
                                      os_password,
                                      os_tenant_name,
                                      os_auth_url,
                                      service_type="volume",
                                      insecure=INSECURE)


  def get_snapshot_list(self,type):
      "print snapshot"
      LOG.info('Start list snapshot ...')
      print "Snapshot Images : "
      for image in self.nova.images.list():
        if image.name.startswith('backup'):
          print " - %s %s" % (image.id, image.name)

      #print self.nova.volumes.list()
      #print self.nova.volume_snapshots.list()
      #print self.cinder.volumes.list()

      print "Snapshot Volumes : "
      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name'

      for volume in self.cinder.volume_snapshots.list():
        #help(volume)
        volume_name=str(getattr(volume, argname))
        print " - %s %s" % (volume.id, volume_name)

  def volume_from_snap_clean(self,id):
      "Clean volume from snapshot"
      LOG.info('Start Clean volume from snapshot ...')
      print "Clean volume from snapshot"
      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name'


      vfs_list={}
      if id == 'all':
        for volume_from_snap in self.cinder.volumes.list():
            volume_from_snap_name=str(getattr(volume_from_snap, argname))
            if volume_from_snap_name.startswith('backup_VFS_'):
                #Remove DATE
                (name, date) = volume_from_snap_name.rsplit('_',1)
                if not name in vfs_list:
                    vfs_list[name] = []
                vfs_list[name].append({'id': volume_from_snap.id, 'date': date})
        self.delete_volumes_from_snap(self.check_for_oldest(vfs_list,VOLUMEFROMSNAP_RET))
      else:
        for volume_from_snap in self.cinder.volumes.list():
            volume_from_snap_name=str(getattr(volume_from_snap, argname))
            if re.search('^backup_.*'+id, volume_from_snap_name):
                (name, date) = volume_from_snap_name.rsplit('_',1)
                if not name in vfs_list:
                    vfs_list[name] = []
                #Add all snap for this volume
                vfs_list[name].append({'id': volume_from_snap.id, 'date': date})
                #print name+' '+str(vfs_list[name])
        self.delete_volumes_from_snap(self.check_for_oldest(vfs_list,VOLUMEFROMSNAP_RET))

  def snap_volume_clean(self,id):
      "clean snapshot"
      LOG.info('Start clean snapshot ...')
      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name'


      volumes_list={}
      if id == 'all':
        for volume_snapshots in self.cinder.volume_snapshots.list():
            volume_name=str(getattr(volume_snapshots, argname))
            if volume_name.startswith('backup_'):
                #Remove DATE
                (name, date) = volume_name.rsplit('_',1)
                if not name in volumes_list:
                    volumes_list[name] = []
                volumes_list[name].append({'id': volume_snapshots.id, 'date': date})
                #print name+' '+str(volumes_list[name])
        self.delete_volumes(self.check_for_oldest(volumes_list,VOLUME_RET))
      else:
        for volume_snapshots in self.cinder.volume_snapshots.list():
            volume_name=str(getattr(volume_snapshots, argname))
            if re.search('^backup_.*'+id, volume_name):
                (name, date) = volume_name.rsplit('_',1)
                if not name in volumes_list:
                    volumes_list[name] = []
                #Add all snap for this volume
                volumes_list[name].append({'id': volume_snapshots.id, 'date': date})
                #print name+' '+str(volumes_list[name])
        self.delete_volumes(self.check_for_oldest(volumes_list,VOLUME_RET))

  def check_for_oldest(self,backup_list,ret):
      "Find useless snapshot"
      print "Find useless snapshot"
      oldest_snapshot = []
      for instance, snapshots in backup_list.iteritems():
        print "  For backup %s" % instance
        #Sort by date (newest to oldest)
        snapshots_sorted=sorted(snapshots, key=lambda x:x['date'], reverse=True)
        print "    %s snapshots to delete" % len(snapshots_sorted[ret:])
        #keep "ret" snapshot for the retention and return the other
        oldest_snapshot += snapshots_sorted[ret:]
      
      #Return snapshot to delete
      return oldest_snapshot

  def delete_volumes(self,volume_snapshots):
      "Delete volume snapshots"
      print "Delete volume snapshots"
      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name'

      for volume_snapshot in volume_snapshots:
          snap=self.cinder.volume_snapshots.get(volume_snapshot['id'])
          snap_name=str(getattr(snap, argname))
          print " - delete %s" % (snap_name)
          if DEBUG == False:
            self.cinder.volume_snapshots.delete(snap)

  def delete_volumes_from_snap(self,volumes_from_snap):
      "Delete volume from snapshots"
      print "Delete volume from snapshots"
      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name'

      for volume_from_snap in volumes_from_snap:
          snap=self.cinder.volumes.get(volume_from_snap['id'])
          snap_name=str(getattr(snap, argname))
          print " - delete %s" % (snap_name)
          if DEBUG == False:
            self.cinder.volumes.delete(snap)

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
      print "Start snapshot image"
      if id == 'all':
        for server in self.nova.servers.list():
          snapname = 'backup_' +server.name+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
          print " - image-snapshot %s" % snapname
          if DEBUG == False:
            server.backup(snapname, 'daily', IMAGE_RET)
      else:
        snapname = 'backup_' +self.nova.servers.get(id).name+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print " - image-snapshot %s" % snapname
        if DEBUG == False:
          self.nova.servers.get(id).backup(snapname, 'daily', IMAGE_RET)


  def snap_volume(self,id):
      "Start volume snapshot"
      print "Start volume snapshot"
      LOG.info('Start volume snapshot ...')
      if id == 'all':
        for volume in self.cinder.volumes.list():
          if volume.status == 'in-use':
            snapname = 'backup_'+self.nova.servers.get(volume.attachments[0]['server_id']).name+'_'+volume.id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            print " - volume-snapshot %s" % snapname
            if DEBUG == False:
              if self.cinder_endpoint_version == '1':
                self.cinder.volume_snapshots.create(volume.id,force=True,display_name=snapname)
              else:
                self.cinder.volume_snapshots.create(volume.id,force=True,name=snapname)
        #fonction clean all
        self.snap_volume_clean('all')
      else:
        snapname = 'backup_' +self.nova.servers.get(self.cinder.volumes.get(id).attachments[0]['server_id']).name+'_'+id+'_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        print " - volume-snapshot %s" % snapname
        if DEBUG == False:
          if self.cinder_endpoint_version == '1':
            self.cinder.volume_snapshots.create(id,force=True,display_name=snapname)
          else:
            self.cinder.volume_snapshots.create(id,force=True,name=snapname)
        #fonction clean
        self.snap_volume_clean(id)

  def volume_from_snap(self,id):
      "Create volumes from snaps"
      LOG.info('Create volumes from snaps ...')
      print "Create volumes from snaps"

      if self.cinder_endpoint_version == '1':
         argname='display_name'
      else:
         argname='name' 

      volumes_list={}

      if id == 'all':
        #search the latest snap to create a volume
        for volume in self.cinder.volume_snapshots.list():
          volume_name=str(getattr(volume, argname))
          if volume_name.startswith('backup_'):
                #Remove DATE
                (name, date) = volume_name.rsplit('_',1)
                if not name in volumes_list:
                        volumes_list[name] = []
                volumes_list[name].append({'id': volume.id, 'date': date, 'size': volume.size})
        #foreach volume take the latest
        for instance, snapshots in volumes_list.iteritems():
                snapshots_sorted=sorted(snapshots, key=lambda x:x['date'], reverse=True)
                #create a volum from the latest snap
                snapname = re.sub("^backup_", 'backup_VFS_', instance)+'_'+snapshots_sorted[0]['date']
                ##CREATE VOLUME
                #print "size %s snapshot_id %s name %s" % (snapshots_sorted[0]['size'], snapshots_sorted[0]['id'], snapname)
                print " - volume-from-snap %s from %s" % (snapname,snapshots_sorted[0]['id'])
                if DEBUG == False:
                  if self.cinder_endpoint_version == '1':
                          self.cinder.volumes.create(snapshots_sorted[0]['size'],snapshot_id=snapshots_sorted[0]['id'],display_name=snapname)
                  else:
                          self.cinder.volumes.create(snapshots_sorted[0]['size'],snapshot_id=snapshots_sorted[0]['id'],name=snapname)
        
        #foreach volume_from_snap
        #check retention for all volume from snap
        self.volume_from_snap_clean('all')
      else:
        #create volume from snapshot_id
        snapshot=self.cinder.volume_snapshots.get(id)
        snapshot_name=str(getattr(snapshot, argname))

        snapname = re.sub("^backup_", 'backup_VFS_', snapshot_name)
        ##CREATE VOLUME
        print " - volume-from-snap %s from %s" % (snapname,id)
        if DEBUG == False:
          if self.cinder_endpoint_version == '1':
                  self.cinder.volumes.create(snapshot.size,snapshot_id=id,display_name=snapname)
          else:
                  self.cinder.volumes.create(snapshot.size,snapshot_id=id,name=snapname)
        ##CREATE VOLUME

        #check retention for volume from snapshot_id
        self.volume_from_snap_clean(id)


if __name__ == "__main__":

   backupmanage = BackupManage(nova_version=ARGS.nova_version,
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

       backupmanage.get_snapshot_list(type=arg_type)
   # Clean snapshot
   elif ARGS.clean:
       if not ARGS.id:
           PARSER.print_help()
           print "Need id param [Error]"
       else:
           backupmanage.snap_volume_clean(id=ARGS.id)
           backupmanage.volume_from_snap_clean(id=ARGS.id)
   # Snapshot
   elif ARGS.snapshot:
       backupmanage.snapshot(type=ARGS.type,id=ARGS.id)
   elif ARGS.volumefromsnap:
       if not ARGS.id:
           PARSER.print_help()
           print "Need id param with all or volume_snapshot_id [Error]"
       else:
           backupmanage.volume_from_snap(id=ARGS.id)
   else:
       PARSER.print_help()
