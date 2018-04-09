<#
This script installs the VMware PowerCLI **BETA** because the production
release doesn't run on PowerShell 6 (which is all I could get running on
Linux in Docker.)
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
