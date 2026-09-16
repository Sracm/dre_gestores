
[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$port = 55192
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Timeout=60;")
$conn.Open()

Write-Host "Exporting 2.Bonificação Clientes from Port $port..."
$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    'Margem de Contribuição'[Item],
    VMQ_DREQLIK[MARGEM],
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[TRIMESTRE],
    DCALENDARIO[SEM],
    VMQ_TSIEMP[RAZAOABREV],
    VMQ_TSICUS[CODCENCUS],
    VMQ_TSICUS[DESCRCENCUS],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(VMQ_CADDRE, VMQ_CADDRE[TITULO] = "2.Bonificação Clientes"),
    "ORCADO", [ORCAMENTO],
    "REALIZADO", [REALIZADO.],
    "VB_ORCADO", [VENDA BRUTA ORCADO],
    "VB_REALIZADO", [VENDA BRUTA REALIZADO]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
Write-Host "Exported $($dt.Rows.Count) rows."

$outCsv = "$PWD\bonif_data_export.csv"
$writer = [System.IO.StreamWriter]::new($outCsv, $false, [System.Text.Encoding]::UTF8)

# Columns order matching dre_data
$cols = @(
    "DCALENDARIO[ANO]",
    "DCALENDARIO[NUMEROMES]",
    "DCALENDARIO[TRIMESTRE]",
    "DCALENDARIO[SEM]",
    "VMQ_TSIEMP[RAZAOABREV]",
    "VMQ_TSICUS[CODCENCUS]",
    "VMQ_TSICUS[DESCRCENCUS]",
    "VMQ_CADDRE[BLOCO]",
    "VMQ_CADDRE[TITULO]",
    "VMQ_TGFNAT[DESCRNAT]",
    "[ORCADO]",
    "[REALIZADO]",
    "[VB_ORCADO]",
    "[VB_REALIZADO]"
)

foreach ($row in $dt.Rows) {
    $vals = @()
    foreach ($col in $cols) {
        $val = $row[$col]
        if ($val -eq [DBNull]::Value -or $val -eq $null) {
            $vals += ""
        } else {
            $vals += $val.ToString().Replace("`t", " ").Replace("`r", "").Replace("`n", "")
        }
    }
    $writer.WriteLine(($vals -join "`t"))
}
$writer.Close()
Write-Host "Saved $outCsv"
$conn.Close()
