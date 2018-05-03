<#
.SYNOPSIS
Saves a full set of annotations obtained from vCenter as a CSV. If there is
already a saved file, the original file is overwritten and a diffs file  is
saved as well.

.DESCRIPTION
This script reads all of its parameters from OS environment variables. It
connects to vCenter and retrieves a complete list of VM annotations and
saves the annotations to /private. If there is a previously saved version,
the script does a diff and passes that off to another script to upload to
Tetration. If there is not a previously saved version, then the script
passes the entire list of annotations off.
#>

<#
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

__author__ = "Doron Chosnek"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"
#>


# ============================================================================
#   GLOBALS
# ----------------------------------------------------------------------------

# the PowerShell -contains switch is case insensitive
$DISPLAY_ON_TEXT = @('on', 'true', '1', 'yes')

# this file is persistent and contains the full inventory of the Datacenter
$INVENTORY_FILE_LOCAL = 'inventory.csv'
$INVENTORY_FILE_DOCKER = '/private/inventory.csv'

# this file is not persistent and contains only diffs from last time the
# script was run; it is non-persistent because it is saved to the local
# filesystem of the container and the container is deleted when it's done
$ANNOTATIONS_DIFF_FILE = 'upload.csv'

# file has list of IP addresses from the AppScope (non-persistent file)
$IP_FILENAME = 'ip.json'

$VM_NAME_ANNOTATION = $env:VM_NAME_ANNOTATION_NAME
$VM_LOCATION_ANNOTATION = $env:VM_LOCATION_ANNOTATION_NAME
$VM_TAGS_ANNOTATION = $env:VM_TAGS_ANNOTATION_NAME
$VM_NETWORKS_ANNOTATION = $env:VM_NETWORKS_ANNOTATION_NAME
$VM_CUSTOM_ATT_ANNOTATION = $env:CUSTOM_ATTRIBUTES_ANNOTATION_NAME
if($DISPLAY_ON_TEXT -contains $env:ENABLE_CUSTOM_ATTRIBUTES) { $ENABLE_CUST_ATT = $true } else { $ENABLE_CUST_ATT = $false }
if($DISPLAY_ON_TEXT -contains $env:ENABLE_VM_NETWORK) { $ENABLE_NETWORKS = $true } else { $ENABLE_NETWORKS = $false }
if($DISPLAY_ON_TEXT -contains $env:ENABLE_VM_TAGS) { $ENABLE_TAGS = $true } else { $ENABLE_TAGS = $false }

# ============================================================================
#   FUNCTIONS
# ----------------------------------------------------------------------------

function SendPigeon {
    <#
    .SYNOPSIS
    Sends feedback to the ecohub portal.

    .PARAMETER Message
    Integer for the status code (100=info, 200=success, 400=failure, etc.)

    .PARAMETER Status
    Text description of the current status.
    #>
        
    Param([string]$Message, [int]$Status)
    $pigeon = @{'status_code'=$Status; 'message'=$Message; 'data'=@{}}

    if ($env:DEBUG) {
        Write-Information -MessageData ($pigeon | ConvertTo-Json -Depth 10) -InformationAction Continue
    }
    else {
        Write-Information -MessageData ($pigeon | ConvertTo-Json -Compress -Depth 10) -InformationAction Continue
    }
}

function Get-CsvDiffs {
    <#
    .SYNOPSIS
    Find the differences between two annotations objects assuming that they
    are in the form of having IP as a unique identifier.
    
    .PARAMETER OldFile
    The contents of the previous annotations CSV file.
    
    .PARAMETER NewFile
    The contents of the new or current CSV file.
    
    .EXAMPLE
    An example
    
    .NOTES
    General notes
    #>
    Param($OldFile, $NewFile)
    # retrieve a list of all properties (CSV column headings) just once as they
    # will be the same for all rows in both files
    if($NewFile) {
        $props = $NewFile | Select-Object -First 1 | 
            Get-Member -MemberType NoteProperty | 
            Select-Object -ExpandProperty Name
    }

    # initialize our return variable as an empty list; we will return only
    # lines that are different
    $diffs = @()

    # Foreach line (row) in the NewFile, we try to find a matching row (search
    # by IP) in the OldFile. If we can't find a match, then we know it's a new
    # IP and should be added to the diffs.
    # If we **CAN** find a match, then we have to walk through every property
    # ($props) and compare the two objects. If any of the properties are not
    # equal, we add the line (row) from the NewFile to our diffs only once.
    foreach ($line in $NewFile) {
        $oldMatch = $OldFile | Where-Object { $_.IP -eq $line.IP }
        if ($oldMatch) {
            $notAdded = $true
            foreach ($p in $props) {
                if ([string]$line.$p -ne [string]$oldMatch.$p -and $notAdded) {
                    $diffs += $line
                    $notAdded = $false
                }
            }
        }
        else {
            $diffs += $line
        }
    }

    return $diffs
}

function Get-VMDetails {
    <#
    .SYNOPSIS
    Retrieve details about a single VM or list of VMs.

    .DESCRIPTION
    Assuming a connection to vCenter, this routine retrieves specified
    information about a VM or list of VMs. The output of this function is
    intended to be sent to a CSV file. The columns to be retrieved are 
    specified as environment variables.

    .PARAMETER Vm
    A PowerCLI VM object or list of VM objects

    .EXAMPLE
    (Get-Datacenter 'Example' | Get-VM) | Get-VMDetails
    #>
    Param([Parameter(Mandatory = $true, ValueFromPipeline = $true)]$Vm,
         [Parameter(Mandatory = $true, ValueFromPipeline = $false)]$Total)

    begin {
        $all_vms = @()
        $counter = 0
        $progress = 10

        # List of all IP addresses in the given VRF or scope as determined by
        # another script (so we just read it from a file)
        $ip_list = Get-Content $IP_FILENAME | ConvertFrom-Json

        # Create a dictionary of network names and PORT GROUP names. Users want to see
        # port group names.
        $network_lookup = @{}
        Get-VDPortgroup | ForEach-Object { $network_lookup[$_.Key] = $_.Name }
    }
    process {

        $counter += 1
        if ($counter / $Total * 100 -ge $progress) {
            SendPigeon -Status 100 -Message "$($progress) percent done looking through vcenter."
            $progress += 10
        }

        # the VM could contain multiple IP addresses, and each one would
        # should be its own annotations entry
        foreach($ip in $Vm.Addresses) {
            
            if($ip -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' -and
                $ip_list -contains $ip) {

                $properties = @{}
                $properties.IP = $ip
                # VRF will be removed later in this script if the environment
                # is multi-tenant, but it's faster to just put it in right now
                # than put it in an 'if' statement in this 'process' block
                $properties.VRF = "Default"

                $properties[$VM_NAME_ANNOTATION] = $Vm.Name
                $properties[$VM_LOCATION_ANNOTATION] = $Vm.VMHost.Name
                
                # Acquiring this property takes a lot of time
                if($ENABLE_TAGS) {
                    $properties[$VM_TAGS_ANNOTATION] = $Vm.Tags
                }

                # Networks is actually a delimited list of every network that
                # the **VM** is connected to. It's not specific to one IP
                # address as most people would hope. That would probably take
                # too long to compute.
                if ($ENABLE_NETWORKS) {
                    $Vm.Networks | % -Begin { $list = @() } -Process {
                        $list += $network_lookup[$_] } -End {
                        $properties[$VM_NETWORKS_ANNOTATION] = ($list -join ";")
                    }
                }

                # save VM Custom Attributes if requested to do so; Custom Attributes
                # are name/value keypair of attributes that can be set per VM
                if ($ENABLE_CUST_ATT) {
                    $Vm.CustomFields | % -Begin { $list = @() } -Process {
                        $list += "$($_.Key)=$($_.Value)" } -End {
                        $properties[$VM_CUSTOM_ATT_ANNOTATION] = ($list -join ";")
                    }
                    
                }

                $all_vms += New-Object -TypeName PSObject -Property $properties

            }
        } # end of "foreach IP" loop
    }     # end of "process" loop
    end {
        return $all_vms
    }
}

# ============================================================================
#   MAIN
# ----------------------------------------------------------------------------

# Set up the headings for the final CSV file. We do that first so that if the
# user forgot to select any annotations columns, we will report an error and
# exit this script without even connecting to vCenter (no reason to hit the
# vCenter API if we aren't going to save any data).

# Stepping through a list of hashes where each hash contains whether or not
# the given annotation is enabled/disabled and what the column name should be.
# This format makes it much easier to add more annotations in the future.

$headings = @()
foreach($h in @(
    @{n=$env:ENABLE_VM_NAME; v=$env:VM_NAME_ANNOTATION_NAME},
    @{n=$env:ENABLE_VM_LOCATION; v=$env:VM_LOCATION_ANNOTATION_NAME},
    @{n=$env:ENABLE_VM_TAGS; v=$env:VM_TAGS_ANNOTATION_NAME},
    @{n=$env:ENABLE_CUSTOM_ATTRIBUTES; v=$env:CUSTOM_ATTRIBUTES_ANNOTATION_NAME},
    @{n=$env:ENABLE_VM_NETWORK; v=$env:VM_NETWORKS_ANNOTATION_NAME} )) 
{
    if($DISPLAY_ON_TEXT -contains $h.n) { $headings += $h.v }
}

# if $headings is still empty, then there is nothing for us to do here (the
# user chose no annotations to upload) and we must:
# 1. Send an error message
# 2. Remove the upload.csv file if one exists
# 3. Exit the script
if ($headings.Length -lt 1) {
    SendPigeon -Status 400 -Message "User must choose at least one attribute for annotations."
    if(Test-Path $ANNOTATIONS_DIFF_FILE) {
        Remove-Item $ANNOTATIONS_DIFF_FILE
    }
    return
}

# Make sure the first column (in multitenant mode) or the first two columns
# (in normal mode) are set properly
if ($DISPLAY_ON_TEXT -contains $env:MULTITENANT) {
    $headings = @("IP") + $headings
}
else {
    $headings = @("IP", "VRF") + $headings
}


# try connecting to vCenter and throw an error if there is a problem; this
# error checking is not robust because ecohub should have already verified
# connectivity using the TEST_CONNECTIVITY action provided by this container

try {
    # Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $false -Confirm:$false
    Connect-VIServer -Server $Env:VCENTER_HOST -User $Env:VCENTER_USER -Password $Env:VCENTER_PWD | Out-Null
}
catch {
    SendPigeon -Status 400 -Message "Error connecting to VCENTER"
    Exit
}

# Set up additional properties that will be available when performing a Get-VM
# cmdlet.The properties created as "ValueFromExtensionProperty" are very
# efficient and do not seem to require additional calls to vCenter.
New-VIProperty -Name ToolsStatus -ObjectType VirtualMachine -ValueFromExtensionProperty 'Guest.ToolsStatus' -Force | Out-Null
New-VIProperty -Name Addresses -ObjectType VirtualMachine -ValueFromExtensionProperty 'Guest.Net.IpAddress' -Force | Out-Null
New-VIProperty -Name Networks -ObjectType VirtualMachine -ValueFromExtensionProperty 'Network.Value' -Force | Out-Null

New-VIProperty -Name Tags -ObjectType VirtualMachine -Value { ($args[0] | Get-TagAssignment | select -ExpandProperty Tag).Name -join ";" } -Force | Out-Null

# determine if we are running in a container or not by checking to see if 
# the directory /private exists...that determines the location of the 
# annotations and date files

if (Test-Path '/private') {
    $INVENTORY_PATH = $INVENTORY_FILE_DOCKER
}
else {
    $INVENTORY_PATH = $INVENTORY_FILE_LOCAL
}

# retrieve the current inventory

$vm_list = (Get-Datacenter $Env:VCENTER_DATACENTER | Get-VM | ? {$_.ToolsStatus -match 'toolsOk'})
SendPigeon -Status 100 -Message "Collecting details from vCenter for $($vm_list.Count) VMs"
$current = $vm_list | Get-VMDetails -Total $vm_list.Count | Select-Object $headings

# Only save entries that have unique IP addresses. If an IP address appears
# more than once, we don't know how to properly annotate it (so we exclude it).

$unique = @()
foreach($blob in $current | Group-Object IP) {
    if($blob.Count -eq 1)
    {
        foreach($entry in $blob.Group) { $unique += $entry }
    }
}

if (Test-Path $INVENTORY_PATH) {

    # if this code is executing, this script has been run before

    SendPigeon -Status 100 -Message "Looking for inventory changes since last run..."
    $previous = Import-Csv $INVENTORY_PATH
    $changes = Get-CsvDiffs -OldFile $previous -NewFile $unique

    $change_count = ($changes | Measure-Object).Count
    SendPigeon -Status 100 -Message "Found $($change_count) annotation changes."
    if($change_count -gt 0) {
        $changes | Select-Object $headings | Export-Csv $ANNOTATIONS_DIFF_FILE -NoTypeInformation
    }
    elseif(Test-Path $ANNOTATIONS_DIFF_FILE) {
        Remove-Item $ANNOTATIONS_DIFF_FILE
    }
}
else {

    # if this code is executing, this script has **NOT** been run before
    SendPigeon -Status 100 -Message "Found $($unique.Count) IP addresses for annotation."
    $unique | Select-Object $headings | Export-Csv $ANNOTATIONS_DIFF_FILE -NoTypeInformation
}

# write the current inventory to disk

$unique | Select-Object $headings | Export-Csv $INVENTORY_PATH -NoTypeInformation

# shut down connection to vCenter

Disconnect-VIServer -Confirm:$false
