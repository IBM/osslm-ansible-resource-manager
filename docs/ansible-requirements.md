# ansible Playbooks and Roles
## Directory Structure
The RM expects to find your ansible resource types (i.e. your playbooks) in a folder in the _resource_ directory.
The folder structure MUST correspond to the naming of the resource type in the resrouce descriptor.

### Example Resource Type Naming
Resource descriptor:
```
name: resource::myres::1.1
```
Folder structure:
```
resources
    myres
       1.1
          myplaybooks.yml
```

## Naming
You **MUST** provide a playbook for each lifecycle transaction and each operation that is specified in your resource de.
Playbooks can make use of roles. The top-level playbook naming is like this:
```
<name of operation>.yml
```
E.g. Install.yml, Start.yml, ...

## Resource ID
Your playboks or roles **MUST** report the resource-id back to the resource manager.
Therefor each playbook or role **MUST** contain one task, that contains the term "RESOURCE_ID" in its name. It should look like:

```yaml
- name: report RESOURCE_ID
  debug:
    msg:
      - "resourceId: {{ os_host['id'] }}"
```
## Resource Properites
**OPTIONALLY** you can report back _PROPERITES_ as a list of key/value pairs. This task can be used multiple times in your playbooks. New properties will simply be appended to the list.
It is you reponsibility to ensure uniqueness of the property-name.

```yaml
- name: report PROPERTIES
  debug:
    msg:
      - "server_name: {{ os_host['name']}}"
      - "mgmt_ip: {{ mgmt_ip }}"
      - "private_ip: {{ private_ip }}"

```
## Internal Resources
**OPTIONALLY** you can report back _INTERNAL RESOURCES_ . This task can be used multiple times in your playbooks. New internal resources will simply be appended to the list.
Each internal resource is described by
- name
- id
- type

```yaml
- name: report INTERNAL_RESOURCE
  debug:
    msg:
     - "name: {{ server['ansible_facts']['openstack_servers'][0]['name'] }}"
     - "id: {{ server['ansible_facts']['openstack_servers'][0]['id'] }}"
     - "type: OS::Nova::Server"
```
