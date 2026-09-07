param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 1514,
    [string]$Message = "configuration change: created firewall rule allow-https"
)

$udp = [System.Net.Sockets.UdpClient]::new()
$timestamp = Get-Date -Format "MMM dd HH:mm:ss"
$syslogMessage = "<134>$timestamp TEST-FIREWALL $Message"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($syslogMessage)

try {
    [void]$udp.Send($bytes, $bytes.Length, $HostName, $Port)
    Write-Host "Syslog message sent to $HostName`:$Port" -ForegroundColor Green
    Write-Host $syslogMessage
}
finally {
    $udp.Dispose()
}
