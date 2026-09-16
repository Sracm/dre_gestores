$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

$ports = @(61526, 61259, 60775, 60117)

foreach ($port in $ports) {
    Write-Host "`n========================================================"
    Write-Host "Checking Port $port"
    Write-Host "========================================================"
    try {
        $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;")
        $conn.Open()
        
        # Get Tables
        $cmdTables = $conn.CreateCommand()
        $cmdTables.CommandText = "SELECT [ID], [Name] FROM `$SYSTEM.TMSCHEMA_TABLES"
        $adapterT = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdTables)
        $dtTables = New-Object System.Data.DataTable
        $adapterT.Fill($dtTables) | Out-Null
        
        $tableNames = @()
        $tableMap = @{}
        foreach ($row in $dtTables.Rows) {
            $tableNames += $row["Name"].ToString()
            $tableMap[$row["ID"].ToString()] = $row["Name"].ToString()
        }
        Write-Host "Tables ($($dtTables.Rows.Count)): $($tableNames -join ', ')"
        
        if ($tableNames -contains "VMQ_DREQLIK" -or $tableNames -contains "VMQ_CADDRE") {
            Write-Host ">>> FOUND DRE MODEL ON PORT $port! <<<"
            
            # Get Measures
            $cmdM = $conn.CreateCommand()
            $cmdM.CommandText = "SELECT [TableID], [Name], [Expression], [FormatString], [Description] FROM `$SYSTEM.TMSCHEMA_MEASURES"
            $adapterM = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdM)
            $dtM = New-Object System.Data.DataTable
            $adapterM.Fill($dtM) | Out-Null
            
            Write-Host "Measures found: $($dtM.Rows.Count)"
            $measures = @()
            foreach ($row in $dtM.Rows) {
                $tid = $row["TableID"].ToString()
                $tname = if ($tableMap.ContainsKey($tid)) { $tableMap[$tid] } else { $tid }
                $mname = $row["Name"].ToString()
                $expr = if ($row["Expression"] -ne $null) { $row["Expression"].ToString() } else { "" }
                $fmt = if ($row["FormatString"] -ne $null) { $row["FormatString"].ToString() } else { "" }
                
                $measures += [PSCustomObject]@{
                    Table = $tname
                    Measure = $mname
                    Expression = $expr
                    FormatString = $fmt
                }
            }
            $measures | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_exact_measures.json" -Encoding utf8
            Write-Host "Successfully exported dre_exact_measures.json!"
            
            # Get Calculated Columns
            $cmdC = $conn.CreateCommand()
            $cmdC.CommandText = "SELECT [TableID], [ExplicitName], [Expression], [Type] FROM `$SYSTEM.TMSCHEMA_COLUMN WHERE [Type] = 2"
            $adapterC = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdC)
            $dtC = New-Object System.Data.DataTable
            $adapterC.Fill($dtC) | Out-Null
            
            $calcCols = @()
            foreach ($row in $dtC.Rows) {
                $tid = $row["TableID"].ToString()
                $tname = if ($tableMap.ContainsKey($tid)) { $tableMap[$tid] } else { $tid }
                $cname = $row["ExplicitName"].ToString()
                $expr = if ($row["Expression"] -ne $null) { $row["Expression"].ToString() } else { "" }
                $calcCols += [PSCustomObject]@{
                    Table = $tname
                    Column = $cname
                    Expression = $expr
                }
            }
            $calcCols | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_exact_calc_columns.json" -Encoding utf8
            Write-Host "Successfully exported dre_exact_calc_columns.json!"
            
            # Get Relationships
            $cmdR = $conn.CreateCommand()
            $cmdR.CommandText = "SELECT [FromTableID], [FromColumnID], [ToTableID], [ToColumnID], [IsActive], [CrossFilteringBehavior] FROM `$SYSTEM.TMSCHEMA_RELATIONSHIP"
            $adapterR = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdR)
            $dtR = New-Object System.Data.DataTable
            $adapterR.Fill($dtR) | Out-Null
            
            # Get Column map
            $cmdCol = $conn.CreateCommand()
            $cmdCol.CommandText = "SELECT [ID], [TableID], [ExplicitName] FROM `$SYSTEM.TMSCHEMA_COLUMN"
            $adapterCol = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmdCol)
            $dtCol = New-Object System.Data.DataTable
            $adapterCol.Fill($dtCol) | Out-Null
            $colMap = @{}
            foreach ($r in $dtCol.Rows) {
                $colMap[$r["ID"].ToString()] = $r["ExplicitName"].ToString()
            }
            
            $rels = @()
            foreach ($r in $dtR.Rows) {
                $fromT = $tableMap[$r["FromTableID"].ToString()]
                $fromC = $colMap[$r["FromColumnID"].ToString()]
                $toT = $tableMap[$r["ToTableID"].ToString()]
                $toC = $colMap[$r["ToColumnID"].ToString()]
                $rels += [PSCustomObject]@{
                    From = "$fromT[$fromC]"
                    To = "$toT[$toC]"
                    IsActive = $r["IsActive"]
                    CrossFiltering = $r["CrossFilteringBehavior"]
                }
            }
            $rels | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_exact_relationships.json" -Encoding utf8
            Write-Host "Successfully exported dre_exact_relationships.json!"
            
            $conn.Close()
            break
        }
        $conn.Close()
    } catch {
        Write-Host "Error: $($_.Exception.Message)"
    }
}
