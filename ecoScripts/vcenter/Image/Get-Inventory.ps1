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


$DISPLAY_ON_TEXT = 'on'

# this file is persistent and contains the full inventory of the Datacenter
$INVENTORY_FILE_LOCAL = 'inventory.csv'
$INVENTORY_FILE_DOCKER = '/private/inventory.csv'

# this file is not persistent and contains only diffs from last time the
# script was run; it is non-persistent because it is saved to the local
# filesystem of the container and the container is deleted when it's done
$ANNOTATIONS_DIFF_FILE = 'upload.csv'

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
    $props = $NewFile | Select-Object -First 1 | 
        Get-Member -MemberType NoteProperty | 
        Select-Object -ExpandProperty Name

    # initialize our return variable as an empty list; we will return only
    # lines that are different
    $diffs = @()

    # Foreach line (row) in the NewFile, we try to find a matching row (search
    # by IP) in the OldFile. If we can't find a match, then we know it's a new
    # IP and should be added to the diffs.
    # If we **CAN** find a match, then we have to walk through every property
    # ($props) and compare the two objects. If any of the properties are not
    # equal, we add the lie (row) from the NewFile to our diffs only once.
    foreach ($line in $NewFile) {
        $oldMatch = $OldFile | Where-Object { $_.IP -eq $line.IP }
        if ($oldMatch) {
            $notAdded = $true
            foreach ($p in $props) {
                if ($line.$p -ne $oldMatch.$p -and $notAdded) {
                    # Write-Host "ERROR $($line.IP) have non-matching $($p)"
                    $diffs += $line
                    $notAdded = $false
                }
            }
        }
        else {
            # Write-Host "$($line.IP) is a new IP"
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
    Assuming a connection to vCenter, this routine retrieves specified information about a VM or list of VMs.
    The output of this function is intended to be sent to a CSV file.
    The columns to be retrieved are specified as environment variables.

    .PARAMETER vm
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
    }
    process {

        $counter += 1
        if ($counter / $Total * 100 -ge $progress) {
            SendPigeon -Status 100 -Message "$($progress) percent done looking through vcenter."
            # $pigeon = @{'status_code'=100; 'message'="$($progress) percent done looking through vcenter."; 'data'=@{}}
            # Write-Information -MessageData ($pigeon | ConvertTo-Json -Compress) -InformationAction Continue
            $progress += 10
        }

        # we don't do anything unless this VM has an IP address
        if ($Vm.Guest.IPAddress[0].Length -gt 6) {

            $properties = @{}
            $properties.IP = $Vm.guest.IPAddress[0]
            $properties.VRF = "Default"

            # save VM name even if it hasn't been requested; it's probably faster to just
            # save it than execute a conditional
            if ($env:VM_NAME_ANNOTATION_NAME -like $DISPLAY_ON_TEXT) {
                $properties[$env:VM_NAME_ANNOTATION_NAME] = $Vm.Name
            }

            # save VM location even if it hasn't been requested
            if ($env:VM_LOCATION_ANNOTATION_NAME -like $DISPLAY_ON_TEXT) {
                $properties[$env:VM_LOCATION_ANNOTATION_NAME] = "$($Vm.VMHost) / $($Vm | Get-Cluster)" 
            }

            # save VM Tags if requested to do so
            if ($env:ENABLE_VM_TAGS -like $DISPLAY_ON_TEXT) {
                $properties[$env:VM_TAGS_ANNOTATION_NAME] = ($Vm | Get-TagAssignment | select -ExpandProperty Tag).Name -join ";"
            }

            # save VM Custom Attributes if requested to do so; Custom Attributes
            # are name/value keypair of attributes that can be set per VM
            if ($env:ENABLE_CUSTOM_ATTRIBUTES -like $DISPLAY_ON_TEXT) {
                $Vm | Get-Annotation | % -Begin {
                    $list = @() } -Process {
                    $list += "$($_.Name)=$($_.Value)" } -End {
                    $properties[$env:CUSTOM_ATTRIBUTES_ANNOTATION_NAME] = ($list -join ";")
                }
            }

            # save VM network if requested to do so
            if ($env:ENABLE_VM_NETWORK -like $DISPLAY_ON_TEXT) {
                $properties[$env:VM_NETWORKS_ANNOTATION_NAME] = ($Vm.Guest.Nics.Device.NetworkName -join ";")
            }

            $all_vms += New-Object -TypeName PSObject -Property $properties

        }
    }
    end {
        return $all_vms
    }
}

# this function is not used anymore
# function Get-VmEvents {
#     Param([Parameter(Mandatory = $true, ValueFromPipeline = $true)]$StartDate)

#     $list = @()

#     foreach ($vm in (Get-Datacenter $env:VCENTER_DATACENTER | Get-VM)) {
#         $events = Get-ViEvent -Entity $vm -Start $StartDate -MaxSamples 1 -Types Info
#         if ($events) {
#             # Write-Host $vm.Name
#             $list += $vm
#         }
#     }
#     # Write-Host $list.Count
#     # Write-Host ($list | select -first 1)
#     return $list
# }

# ============================================================================
#   MAIN
# ----------------------------------------------------------------------------

# determine if we are running in a container or not by checking to see if 
# the directory /private exists...that determines the location of the 
# annotations and date files

if (Test-Path '/private') {
    $INVENTORY_PATH = $INVENTORY_FILE_DOCKER
}
else {
    $INVENTORY_PATH = $INVENTORY_FILE_LOCAL
}

# try connect to vCenter and throw an error if there is a problem

try {
    # Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $false -Confirm:$false
    Connect-VIServer -Server $Env:VCENTER_HOST -User $Env:VCENTER_USER -Password $Env:VCENTER_PWD | Out-Null
}
catch {
    SendPigeon -Status 400 -Message "Error connecting to VCENTER"
    Exit
}

# set up the headings that we want in our final CSV; we have to do this here so that
# they appear in the right order
$headings = @("IP", "VRF")
if ($env:ENABLE_VM_NAME) {
    if ($env:ENABLE_VM_NAME -like $DISPLAY_ON_TEXT) {
        $headings += $env:VM_NAME_ANNOTATION_NAME
    }
}
if ($env:ENABLE_VM_LOCATION) {
    if ($env:ENABLE_VM_LOCATION -like $DISPLAY_ON_TEXT) {
        $headings += $env:VM_LOCATION_ANNOTATION_NAME
    }
}
if ($env:ENABLE_VM_TAGS) {
    if ($env:ENABLE_VM_TAGS -like $DISPLAY_ON_TEXT) {
        $headings += $env:VM_TAGS_ANNOTATION_NAME
    }
}
if ($env:ENABLE_CUSTOM_ATTRIBUTES) {
    if ($env:ENABLE_CUSTOM_ATTRIBUTES -like $DISPLAY_ON_TEXT) {
        $headings += $env:CUSTOM_ATTRIBUTES_ANNOTATION_NAME
    }
}
if ($env:ENABLE_VM_NETWORK) {
    if ($env:ENABLE_VM_NETWORK -like $DISPLAY_ON_TEXT) {
        $headings += $env:VM_NETWORKS_ANNOTATION_NAME
    }
}

# retrieve the current inventory regardless

$count = (Get-Datacenter $Env:VCENTER_DATACENTER | Get-VM).Count
SendPigeon -Status 100 -Message "Collecting details for all $($count) VMs..."

$vm_list = (Get-Datacenter $Env:VCENTER_DATACENTER | Get-VM)
$current = $vm_list | Get-VMDetails -Total $vm_list.Count

if (Test-Path $INVENTORY_PATH) {

    SendPigeon -Status 100 -Message "Looking for inventory changes since last run..."
    $previous = Import-Csv $INVENTORY_PATH
    $changes = Get-CsvDiffs -OldFile $previous -NewFile $current
    
}
else {
    
    SendPigeon -Status 100 -Message "Saving details for all $($count) VMs..."
    $changes = $current
}

# write the current inventory to disk

$current | Select-Object $headings | Export-Csv $INVENTORY_PATH -NoTypeInformation

# write out the CSV so the next script can post to TA; the diffs file contains
# diffs if there were diffs... otherwise it contains the entire inventory
$change_count = ($changes | Measure-Object).Count
if ($change_count -gt 0) {
    $changes | Select-Object $headings | Export-Csv $ANNOTATIONS_DIFF_FILE -NoTypeInformation
    SendPigeon -Status 100 -Message "Found $($change_count) annotations."
}
else {
    $current | Select-Object $headings | Export-Csv $ANNOTATIONS_DIFF_FILE -NoTypeInformation
    SendPigeon -Status 100 -Message "Did not find any updated annotations."
}

# shut down connection to vCenter

Disconnect-VIServer -Confirm:$false
