$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60775;")
$conn.Open()

# Query TMSCHEMA_PARTITION or MDSCHEMA to get calculated tables M queries and DAX
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT [TableID], [Name], [SourceType], [QueryDefinition] FROM `$SYSTEM.TMSCHEMA_PARTITION"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$cmdT = $conn.CreateCommand()
$cmdT.CommandText = "SELECT [ID], [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
$adapterT = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdT)
$dtT = New-Object System.Data.DataTable
$adapterT.Fill($dtT) | Out-Null
$tableMap = @{}
foreach ($r in $dtT.Rows) { $tableMap[$r["ID"].ToString()] = $r["Name"].ToString() }

$partitions = @()
foreach ($r in $dt.Rows) {
    $tname = $tableMap[$r["TableID"].ToString()]
    $pname = $r["Name"].ToString()
    $qdef = if ($r["QueryDefinition"] -ne $null) { $r["QueryDefinition"].ToString() } else { "" }
    $partitions += [PSCustomObject]@{
        Table = $tname
        Partition = $pname
        Type = $r["SourceType"]
        Query = $qdef
    }
}
$partitions | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_partitions_m_dax.json" -Encoding utf8
Write-Host "Saved dre_partitions_m_dax.json ($($partitions.Count) partitions)"

# Query TMSCHEMA_COLUMN to get calculated column expressions
$cmdC = $conn.CreateCommand()
$cmdC.CommandText = "SELECT [TableID], [ExplicitName], [Expression], [Type] FROM `$SYSTEM.TMSCHEMA_COLUMN"
$adapterC = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdC)
$dtC = New-Object System.Data.DataTable
$adapterC.Fill($dtC) | Out-Null

$cols = @()
foreach ($r in $dtC.Rows) {
    $tname = $tableMap[$r["TableID"].ToString()]
    $cname = $r["ExplicitName"].ToString()
    $expr = if ($r["Expression"] -ne $null) { $r["Expression"].ToString() } else { "" }
    if ($expr -ne "") {
        $cols += [PSCustomObject]@{
            Table = $tname
            Column = $cname
            Expression = $expr
        }
    }
}
$cols | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_calculated_columns.json" -Encoding utf8
Write-Host "Saved dre_calculated_columns.json ($($cols.Count) calculated columns)"

$conn.Close()
