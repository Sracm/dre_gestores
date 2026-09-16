$dll = "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.Tabular.dll"
[System.Reflection.Assembly]::LoadFrom($dll) | Out-Null

$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:60775")
$model = $server.Databases[0].Model

Write-Host "Connected to Tabular Model: $($server.Databases[0].Name)"

# Export all tables, columns (including calculated), partitions (M and DAX)
$export = @{
    Tables = @()
    Relationships = @()
}

foreach ($t in $model.Tables) {
    $tinfo = @{
        Name = $t.Name
        Columns = @()
        Partitions = @()
        Measures = @()
    }
    foreach ($c in $t.Columns) {
        $cinfo = @{
            Name = $c.Name
            Type = $c.Type.ToString()
            DataType = $c.DataType.ToString()
        }
        if ($c.Type -eq "Calculated") {
            $cinfo["Expression"] = $c.Expression
        }
        $tinfo.Columns += $cinfo
    }
    foreach ($p in $t.Partitions) {
        $tinfo.Partitions += @{
            Name = $p.Name
            SourceType = $p.SourceType.ToString()
            Query = if ($p.Source -ne $null) { $p.Source.Expression } else { "" }
        }
    }
    foreach ($m in $t.Measures) {
        $tinfo.Measures += @{
            Name = $m.Name
            Expression = $m.Expression
            FormatString = $m.FormatString
        }
    }
    $export.Tables += $tinfo
}

foreach ($r in $model.Relationships) {
    $export.Relationships += @{
        FromTable = $r.FromTable.Name
        FromColumn = $r.FromColumn.Name
        ToTable = $r.ToTable.Name
        ToColumn = $r.ToColumn.Name
        IsActive = $r.IsActive
        CrossFilteringBehavior = $r.CrossFilteringBehavior.ToString()
    }
}

$export | ConvertTo-Json -Depth 6 | Out-File -FilePath "dre_tabular_model_full.json" -Encoding utf8
Write-Host "Successfully generated dre_tabular_model_full.json!"

$server.Disconnect()
