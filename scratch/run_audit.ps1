[System.Reflection.Assembly]::LoadFrom("C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && (DCALENDARIO[NUMEROMES] = 8 || DCALENDARIO[NUMEROMES] = 9)),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$conn.Close()

$rows = @()
foreach ($r in $dt.Rows) {
    $rows += [PSCustomObject]@{
        mes = [int]$r["DCALENDARIO[NUMEROMES]"]
        bloco = [string]$r["VMQ_CADDRE[BLOCO]"]
        titulo = [string]$r["VMQ_CADDRE[TITULO]"]
        descrnat = [string]$r["VMQ_TGFNAT[DESCRNAT]"]
        orcado = if ($r["[ORCADO]"] -ne [DBNull]::Value) { [double]$r["[ORCADO]"] } else { 0.0 }
        realizado = if ($r["[REALIZADO]"] -ne [DBNull]::Value) { [double]$r["[REALIZADO]"] } else { 0.0 }
    }
}
$rows | ConvertTo-Json -Depth 3 | Out-File -FilePath "$PWD/scratch/pbi_audit_m8_m9.json" -Encoding utf8
Write-Host "Done. Total rows:" $rows.Count
