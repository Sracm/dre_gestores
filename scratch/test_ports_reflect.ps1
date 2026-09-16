# Use the same pattern that populate_dre_detalhe_fsp_fast.py uses (Microsoft.AnalysisServices.AdomdClient)
$dll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($dll) | Out-Null

# List assemblies loaded
[System.AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.FullName -like "*Adomd*" -or $_.FullName -like "*PowerBI*" } | Select-Object FullName

foreach ($port in @(49676, 57430)) {
    Write-Host "Testando porta $port..."
    try {
        $type = [System.AppDomain]::CurrentDomain.GetAssemblies() | 
                ForEach-Object { try { $_.GetType("Microsoft.PowerBI.AdomdClient.AdomdConnection") } catch {} } | 
                Where-Object { $_ -ne $null } | Select-Object -First 1
        
        if ($null -eq $type) {
            Write-Host "  Tipo nao encontrado nos assemblies"
            break
        }
        
        $conn = [System.Activator]::CreateInstance($type, @("Data Source=localhost:$port"))
        $openMethod = $type.GetMethod("Open")
        $openMethod.Invoke($conn, $null)
        Write-Host "  => CONEXAO OK porta $port" -ForegroundColor Green
        $type.GetMethod("Close").Invoke($conn, $null)
    } catch {
        $msg = $_.Exception.InnerException.Message
        if (!$msg) { $msg = $_.Exception.Message }
        if ($msg.Length -gt 200) { $msg = $msg.Substring(0, 200) }
        Write-Host "  => FALHA $port : $msg"
    }
}
