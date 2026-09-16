$ports = @(61526, 61259, 60775, 60117)

foreach ($port in $ports) {
    Write-Host "`n=== Testing Port: $port ==="
    try {
        $connStr = "Provider=MSOLAP;Data Source=localhost:$port;"
        $conn = New-Object System.Data.OleDb.OleDbConnection($connStr)
        $conn.Open()
        Write-Host "CONNECTED to port $port!"
        
        # Get Database Name
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT [CATALOG_NAME], [DATE_MODIFIED] FROM `$SYSTEM.DBSCHEMA_CATALOGS"
        $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($cmd)
        $dt = New-Object System.Data.DataTable
        $adapter.Fill($dt) | Out-Null
        $dbName = $dt.Rows[0]["CATALOG_NAME"]
        Write-Host "Database Name: $dbName"
        
        # Get all measures!
        $cmd2 = $conn.CreateCommand()
        $cmd2.CommandText = "SELECT [TABLE_NAME], [MEASURE_NAME], [EXPRESSION], [DESCRIPTION] FROM `$SYSTEM.MDSCHEMA_MEASURES"
        $dt2 = New-Object System.Data.DataTable
        $adapter2 = New-Object System.Data.OleDb.OleDbDataAdapter($cmd2)
        $adapter2.Fill($dt2) | Out-Null
        
        Write-Host "Found $($dt2.Rows.Count) measures in this model!"
        
        # Check if this model contains VMQ_DREQLIK or DRE measures
        $hasDre = $false
        $measureList = @()
        foreach ($row in $dt2.Rows) {
            $expr = $row["EXPRESSION"]
            $mname = $row["MEASURE_NAME"]
            $tname = $row["TABLE_NAME"]
            if ($expr) {
                if ($mname -like "*REALIZADO*" -or $mname -like "*ORCADO*" -or $tname -like "*DRE*") {
                    $hasDre = $true
                }
                $measureList += [PSCustomObject]@{
                    Table = $tname
                    Measure = $mname
                    Expression = $expr
                }
            }
        }
        
        if ($hasDre) {
            Write-Host ">>> THIS IS THE DRE MODEL! ($($measureList.Count) measures)"
            $measureList | ConvertTo-Json -Depth 5 | Out-File -FilePath "pbi_dre_measures.json" -Encoding utf8
            Write-Host "Exported to pbi_dre_measures.json!"
            
            # Also export tables and relationships!
            $cmd3 = $conn.CreateCommand()
            $cmd3.CommandText = "SELECT [DIMENSION_NAME] FROM `$SYSTEM.MDSCHEMA_DIMENSIONS"
            $dt3 = New-Object System.Data.DataTable
            $adapter3 = New-Object System.Data.OleDb.OleDbDataAdapter($cmd3)
            $adapter3.Fill($dt3) | Out-Null
            $tables = @()
            foreach ($row in $dt3.Rows) {
                $tables += $row["DIMENSION_NAME"]
            }
            Write-Host "Tables in Model: $($tables -join ', ')"
            
            # Also export calculated columns (TMSL or DMV)
            try {
                $cmd4 = $conn.CreateCommand()
                $cmd4.CommandText = "SELECT [TableID], [ExplicitName], [Expression] FROM `$SYSTEM.TMSCHEMA_COLUMN WHERE [Type] = 2"
                $dt4 = New-Object System.Data.DataTable
                $adapter4 = New-Object System.Data.OleDb.OleDbDataAdapter($cmd4)
                $adapter4.Fill($dt4) | Out-Null
                $calcCols = @()
                foreach ($r in $dt4.Rows) {
                    $calcCols += [PSCustomObject]@{
                        Column = $r["ExplicitName"]
                        Expression = $r["Expression"]
                    }
                }
                $calcCols | ConvertTo-Json -Depth 5 | Out-File -FilePath "pbi_calc_columns.json" -Encoding utf8
                Write-Host "Exported calculated columns to pbi_calc_columns.json!"
            } catch {
                Write-Host "Could not query TMSCHEMA_COLUMN: $($_.Exception.Message)"
            }

            $conn.Close()
            break
        } else {
            Write-Host "Not the DRE model (measures: $($dt2.Rows.Count))"
        }
        
        $conn.Close()
    }
    catch {
        Write-Host "Failed port $port : $($_.Exception.Message)"
    }
}
