$adomdPath = "C:\Program Files\Microsoft.NET\ADOMD.NET\160\Microsoft.AnalysisServices.AdomdClient.dll"
Add-Type -Path $adomdPath

$ports = @(60110, 63282, 63312, 58611, 57197, 52302, 52313, 52314, 52315, 52331, 53323, 51845, 61048, 58969, 58970)

foreach ($port in $ports) {
    try {
        $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port")
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "EVALUATE {1}"
        $reader = $cmd.ExecuteReader()
        $conn.Close()
        Write-Host "==> PORTA ATIVA: $port" -ForegroundColor Green
    } catch {
        $msg = $_.Exception.Message.Split([char]13)[0].Substring(0, [Math]::Min(80, $_.Exception.Message.Length))
        Write-Host "Porta $port FAIL: $msg"
    }
}
