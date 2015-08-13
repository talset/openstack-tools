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

Help :

```bash
python snapshot/snapshot.py -h
usage: snapshot.py [-h] [-osti OS_TENANT_ID] [-ostn OS_TENANT_NAME]
                   [-osu OS_USERNAME] [-osp OS_PASSWORD] [-osurl OS_AUTH_URL]
                   [-nv NOVA_VERSION] [-l] [-c] [-s] [-vfs] [-t TYPE] [-i ID]

optional arguments:
  -h, --help            show this help message and exit
  -osti OS_TENANT_ID, --os-tenant-id OS_TENANT_ID
                        Tenant to request authorization on. Defaults to
                        env[OS_TENANT_ID]
  -ostn OS_TENANT_NAME, --os-tenant-name OS_TENANT_NAME
                        Tenant to request authorization on. Defaults to
                        env[OS_TENANT_NAME]
  -osu OS_USERNAME, --os-username OS_USERNAME
                        Name used for authentication with the OpenStack
                        Identity service. Defaults to env[OS_USERNAME]
  -osp OS_PASSWORD, --os-password OS_PASSWORD
                        Password used for authentication with the OpenStack
                        Identity service. Defaults to env[OS_PASSWORD]
  -osurl OS_AUTH_URL, --os-auth-url OS_AUTH_URL
                        Specify the Identity endpoint to use for
                        authentication. Defaults to env[OS_AUTH_URL]
  -nv NOVA_VERSION, --nova-version NOVA_VERSION
                        Nova client version. Defaults to 2
  -l, --list            print snapshot
  -c, --clean           clean snapshot
  -s, --snapshot        Start snapshot
  -vfs, --volumefromsnap
                        Create a volume from the last volume_snapshot (--id
                        need to be a volume_snapshot id
  -t TYPE, --type TYPE  type of snapshot (ex : image|volume|all)
  -i ID, --id ID        id to backup (ex : <id_image>|<id_volume>|all)
```

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
