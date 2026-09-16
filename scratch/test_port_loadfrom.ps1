$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdPath) | Out-Null

$port = 49676
Write-Host "Testando porta $port (DESENV. PRODUTOS)..."

try {
    $connType = [System.Reflection.Assembly]::LoadFrom($adomdPath).GetType("Microsoft.PowerBI.AdomdClient.AdomdConnection")
    $conn = [System.Activator]::CreateInstance($connType, "Data Source=localhost:$port")
    $conn.Open()
    Write-Host "CONEXAO OK na porta $port" -ForegroundColor Green
    $conn.Close()
} catch {
    Write-Host "FALHA: $($_.Exception.Message.Substring(0, [Math]::Min(300, $_.Exception.Message.Length)))"
}

# Also test port 57430
$port2 = 57430
Write-Host "Testando porta $port2..."
try {
    $conn2 = [System.Activator]::CreateInstance($connType, "Data Source=localhost:$port2")
    $conn2.Open()
    Write-Host "CONEXAO OK na porta $port2" -ForegroundColor Green
    $conn2.Close()
} catch {
    Write-Host "FALHA $port2: $($_.Exception.Message.Substring(0, [Math]::Min(200, $_.Exception.Message.Length)))"
}
