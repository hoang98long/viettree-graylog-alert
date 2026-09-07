$scriptPath = Join-Path $PSScriptRoot "send-graylog.ps1"
& $scriptPath -Message "configuration change: created firewall rule allow-https"
