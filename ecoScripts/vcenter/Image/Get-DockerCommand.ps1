
$IMAGE_NAME = 'ecohub/vcenter'
$VOLUME_NAME = 'ecohub-vcenter'
$VERSION_NUM = 'v0.3'
$linux = @()
$docker = @()

foreach($p in (Get-Content env.json | ConvertFrom-Json).PSObject.Properties) {
    
    # collect the ENV variables in Linux format 
    $linux += "export $($p.Name)='$($p.Value)'"

    # collect the ENV variables in Docker format
    $docker += "-e $($p.Name)='$($p.Value)'"

    # set the environment variable in the local window
    $key = $p.Name
    Set-Item env:\$key -Value $p.Value
}

$cmd = 'docker run --rm -it ' + ($docker -join ' ') + " -v $($VOLUME_NAME):/private $($IMAGE_NAME):$($VERSION_NUM)"

Write-Host "Linux format environment variables"
Write-Host "=================================="

Write-Host ($linux -join "`r`n" | Out-String)

Write-Host ""
Write-Host "Docker command (also in clipboard"
Write-Host "=================================="

Write-Host $cmd

if($PSVersionTable.PSVersion.Major -le 5) {
    $cmd | Set-Clipboard
}
else {
    $cmd | pbcopy
}