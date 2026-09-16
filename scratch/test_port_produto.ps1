$adomdPath = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
Add-Type -Path $adomdPath

$port = 49676
Write-Host "Testando porta $port (DESENV. PRODUTOS)..."

try {
    $conn = New-Object Microsoft.PowerBI.AdomdClient.AdomdConnection("Data Source=localhost:$port")
    $conn.Open()
    $cmd = $conn.CreateCommand()
    # List tables available
    $cmd.CommandText = "EVALUATE {1}"
    $reader = $cmd.ExecuteReader()
    $conn.Close()
    Write-Host "CONEXAO OK na porta $port" -ForegroundColor Green
} catch {
    Write-Host "FALHA porta $port : $($_.Exception.Message.Substring(0, [Math]::Min(200, $_.Exception.Message.Length)))"
}
