$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
Add-Type -Path $adomdPath

$allPorts = (Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -gt 49000 -and $_.LocalPort -lt 65000} | Select-Object -ExpandProperty LocalPort | Sort-Object -Unique)

Write-Host "Testando $($allPorts.Count) portas..."

foreach ($port in $allPorts) {
    try {
        $conn = New-Object Microsoft.PowerBI.AdomdClient.AdomdConnection("Data Source=localhost:$port")
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "EVALUATE {1}"
        $reader = $cmd.ExecuteReader()
        $conn.Close()
        Write-Host "==> PORTA ATIVA PBI: $port" -ForegroundColor Green
    } catch {
        # Silent fail
    }
}
Write-Host "Teste concluido."
