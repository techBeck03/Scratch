<#
This script installs the VMware PowerCLI **BETA** because the production
release doesn't run on PowerShell 6 (which is all I could get running on
Linux in Docker.)

"""
This script originally tested connectivity to both Cisco Tetration and VMware
vCenter endpoints, but the Tetration test has been moved to another part of
the ecohub project. This code now only tests vCenter connectivity.
The bulk of the work is handling all of the errors that might arise.

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
#>

# to avoid prompts, set the PSGallery to be a trusted repository

Set-PSRepository -Name PSGallery -InstallationPolicy Trusted

# installing the BETA of PowerCLI using instructions from here:
# https://communities.vmware.com/docs/DOC-37537

$installOrder = @(  
    "VMware.VimAutomation.Sdk",  
    "VMware.VimAutomation.Common",  
    "VMware.VimAutomation.Cis.Core",  
    "VMware.VimAutomation.Core",  
    "VMware.VimAutomation.License",  
    "VMware.VimAutomation.Vds",  
    "VMware.VimAutomation.Storage",  
    "VMware.VimAutomation.Cloud",  
    "VMware.VimAutomation.vROps",  
    "VMware.VimAutomation.PCloud",  
    "VMware.VimAutomation.Nsxt",  
    "VMware.VimAutomation.vmc"  
) 

# added the -confirm:$false option for non-interactive installation
$installOrder | %{Install-Module $_ -AllowPrerelease -Repository PSGallery -confirm:$false}

# and we ignore certificate warnings
# http://www.pragmaticio.com/2015/01/vmware-powercli-suppress-vcenter-certificate-warnings/
Set-PowerCLIConfiguration -InvalidCertificateAction ignore -confirm:$false

# do not participate in VMware Customer Experience Improvement Program ("CEIP")
# as we can't make the assumption for every user of this container that they
# would want to do that
Set-PowerCLIConfiguration -Scope AllUsers -ParticipateInCeip $false -Confirm:$false
