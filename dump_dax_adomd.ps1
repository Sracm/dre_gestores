$adomdDll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null
Write-Host "Loaded AdomdClient assembly successfully."

$ports = @(61526, 61259, 60775, 60117)

foreach ($port in $ports) {
    Write-Host "`n=== Checking Port $port ==="
    try {
        $connStr = "Data Source=localhost:$port;"
        $conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
        $conn.Open()
        Write-Host "Successfully connected to port $port!"
        
        # Check databases
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT [CATALOG_NAME] FROM `$SYSTEM.DBSCHEMA_CATALOGS"
        $reader = $cmd.ExecuteReader()
        $catName = ""
        while ($reader.Read()) {
            $catName = $reader[0].ToString()
            Write-Host "Database: $catName"
        }
        $reader.Close()
        
        # Query MDSCHEMA_MEASURES
        $cmd.CommandText = "SELECT [TABLE_NAME], [MEASURE_NAME], [EXPRESSION] FROM `$SYSTEM.MDSCHEMA_MEASURES"
        $reader = $cmd.ExecuteReader()
        $measures = @()
        $isDre = $false
        while ($reader.Read()) {
            $t = $reader["TABLE_NAME"].ToString()
            $m = $reader["MEASURE_NAME"].ToString()
            $e = if ($reader["EXPRESSION"] -ne $null) { $reader["EXPRESSION"].ToString() } else { "" }
            
            if ($m -like "*REALIZADO*" -or $m -like "*ORCADO*" -or $t -like "*DRE*" -or $m -like "*MARGEM*") {
                $isDre = $true
            }
            if ($e -ne "") {
                $measures += [PSCustomObject]@{
                    Table = $t
                    Measure = $m
                    Expression = $e
                }
            }
        }
        $reader.Close()
        
        if ($isDre) {
            Write-Host ">>> FOUND DRE MODEL ON PORT $port! ($($measures.Count) measures with expressions)"
            $measures | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_dax_measures_exact.json" -Encoding utf8
            Write-Host "Saved dre_dax_measures_exact.json!"
            
            # Query TMSCHEMA_COLUMN (Calculated Columns)
            try {
                $cmd.CommandText = "SELECT [TableID], [ExplicitName], [Expression] FROM `$SYSTEM.TMSCHEMA_COLUMN WHERE [Type] = 2"
                $reader = $cmd.ExecuteReader()
                $calcCols = @()
                while ($reader.Read()) {
                    $cname = $reader["ExplicitName"].ToString()
                    $cexpr = if ($reader["Expression"] -ne $null) { $reader["Expression"].ToString() } else { "" }
                    $calcCols += [PSCustomObject]@{
                        Column = $cname
                        Expression = $cexpr
                    }
                }
                $reader.Close()
                $calcCols | ConvertTo-Json -Depth 5 | Out-File -FilePath "dre_calc_columns_exact.json" -Encoding utf8
                Write-Host "Saved dre_calc_columns_exact.json!"
            } catch {
                Write-Host "Error getting calc columns: $($_.Exception.Message)"
            }

            # Query TMSCHEMA_RELATIONSHIP (Model Relationships)
            try {
                $cmd.CommandText = "SELECT * FROM `$SYSTEM.TMSCHEMA_RELATIONSHIP"
                $reader = $cmd.ExecuteReader()
                Write-Host "Relationships query executed."
                $reader.Close()
            } catch {}

            $conn.Close()
            break
        }
        $conn.Close()
    }
    catch {
        Write-Host "Error on port $port : $($_.Exception.Message)"
    }
}
