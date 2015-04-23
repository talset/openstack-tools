openstack-tools
===============

little script to do some actions with clientlib


#snapshot

##snapshot.py

prerequisite
```bash
apt-get install git python-cinderclient python-novaclient
```

Set the retention to keep
```bash
IMAGE_RET=7 #kepp 7 latest snapshot (nova)
VOLUME_RET=7 #kepp 7 latest snapshot volume (cinder)
VOLUMEFROMSNAP_RET=1 #kepp 1 latest volume from volumesnapshot (cinder)
```

Run with crontab
```bash
#Create snapshot (instances and volumes) all days at 3h00  
0 3 * * * python /opt/openstack-tools/snapshot/snapshot.py --os-tenant-id tenantid --os-tenant-name "tenantname" --os-username "username" --os-password password --os-auth-url https://identity/v2.0 --snapshot --type all --id all  
  
#Create volumes from volume_snapshot all monday at 7h00  
0 7 1 * * python /opt/openstack-tools/snapshot/snapshot.py --os-tenant-id tenantid --os-tenant-name "tenantname" --os-username "username" --os-password password --os-auth-url https://identity/v2.0 -vfs --id all
```

###Exemple of use

Made nova image-create (snapshot) of all vms
```bash
python snapshot.py  --snapshot --type image --id all
```

Made cinder snapshot of all volumes
```bash
python snapshot.py --snapshot --type volume --id all
```

Made image-create and cinder snapshot
```bash
python snapshot.py --snapshot --type all --id all
```

Create a volume from the latest volume_snapshot (for all volumes)
```bash
python snapshot.py -vfs --id all
```
