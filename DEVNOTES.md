# Library Panels
Library Panels created rely on a uid. When loading a panel through the grafana API in v9 and v10, the content of the model component of the json is critical. 
To ensure that panels are reusable, the model section MUST have a ```libraryPanel``` section that looks like this

```
"model": {
    ...
    "libraryPanel": {
        "name": "Panel name or title",
        "uid": "unique UUID"
    }
    ...
}
```
This structure is not 100% honored out of the box in Grafana 9 and 10, so to ensure the dashboards and panels can be reused within this project, the panel JSON must be modified to align to this requirement.

The ```fixes``` directory contains examples of the code used to post process the panel json files to meet the above spec.

The ```extract-panels.py``` script provides the ability to extract panels from a Grafana instance, which you can then push into the playbooks hierarchy. The resulting panel json is sanitised to ensure the model section contains a libraryPanel component.

# Exporting Dashboards
When you want to export a dashboard that may be imported into another deployment of the ceph-monitoring project, remember to export select the "Export for sharing externally" toggle switch on the Share > Export modal dialog.

# Ansible Collections
The playbooks use the ansible.posix.firewalld module which may not be installed on your system by default. To fix;
```
# ansible-galaxy collection install ansible.posix
```
