## ![alt text](https://github.com/techBeck03/Scratch/raw/master/ecoScripts/vcenter/icon.png "Logo") vCenter Annotations

### Overview
The vCenter integration generates user annotations for your Tetration deployment based on rich data pulled from a single datacenter in vCenter.

ecohub users can selectively annotate based on any number of the following properties:

- VM Name
- VM Location (host and cluster)
- VM Network
- vSphere Tags
- VM Custom Attributes

The integration will always get the IP address for each VM.

### Behavior

The first time the deployment executes, it retrieves all of the desired information about every virtual machine in the specified Datacenter. It then pushes that data to Tetration, including only information about virtual machines that have a valid IP address. *Note that vCenter can only report the IP address for virtual machines running VMware Tools.*

Each subsequent time the deployment executes, it still retrieves information about every virtual machine in the specified Datacenter, but it only pushes *changes* to Tetration.

To force the deployment to push a complete copy of annotations to Tetration again, click the `"Clear Cache"` button in the configuration screen for the deployment.

### Configuration

This section desribes how to configure a **deployment** of the vCenter Annotations image. There are two sections of configuration parameters.

#### Connection Parameters

- **vCenter** is the hostname or IP address for vCenter. Do not include HTTP or HTTPS in this field.
- **VC Username** specifies the login ID to be used each time this deployment runs. Use an account with read access to the vCenter and datacenter that chosen.
- **VC Password** is the login password for the username specified above. ecohub uses this password to connect to vCenter every time, this field must be updated if the user's password changes.
- **VC Datacenter** defines the vCenter Datacenter object from which to pull data. If information from more than one Datacenter is required, simply create multiple deployments of the vCenter image (more details below).

#### Annotation Options

- **VM Name** is a toggle switch that determines if the virtual machine name is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for VM Name can be customized. More details are provided below.
- **VM Location** is a toggle switch that determines if the virtual machine location is included in annotations pushed to Tetration. VM location is specified in the format: `"host / cluster`". When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **VM Tags** is a toggle switch that determines if the vSphere tag for a virtual machine is included in the annotations pushed to Tetration. A tag is a label that you can apply to objects in the vSphere inventory. When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **Custom Attributes** is a toggle switch that determines if a virtual machine's custom attributes are included in the annotations pushed to Tetration. Custom attributes are key:value pairs that can be applied to virtual machines and searched upon in Tetration. When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **VM Networks** is a toggle switch that determines if the names of the networks (port groups) for each virtual machine are included in the annotations pushed to Tetration. When this toggle is on, the name of the annotation used for the VM Networks can be customized. More details are provided below.

### Multiple Datacenters

some text goes here

### Renaming attributes