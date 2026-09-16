import subprocess, json

ps_script = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:53301;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    DCALENDARIO[TRI ANO],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    VW_MQ_TGFPAR_POWER_BI[NOME],
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$rows = @()
foreach ($r in $dt.Rows) {
    $rows += [PSCustomObject]@{
        ano = [int]$r["DCALENDARIO[ANO]"]
        mes = [int]$r["DCALENDARIO[NUMEROMES]"]
        nomemes = [string]$r["DCALENDARIO[NOMEMES]"]
        tri_ano = [string]$r["DCALENDARIO[TRI ANO]"]
        bloco = [string]$r["VMQ_CADDRE[BLOCO]"]
        titulo = [string]$r["VMQ_CADDRE[TITULO]"]
        descrnat = [string]$r["VMQ_TGFNAT[DESCRNAT]"]
        parceiro = [string]$r["VW_MQ_TGFPAR_POWER_BI[NOME]"]
        orcado = if ($r["ORCADO"] -ne [DBNull]::Value) { [double]$r["ORCADO"] } else { 0.0 }
        realizado = if ($r["REALIZADO"] -ne [DBNull]::Value) { [double]$r["REALIZADO"] } else { 0.0 }
    }
}
$conn.Close()

$rows | ConvertTo-Json -Depth 3 | Out-File -FilePath "$PWD/scratch/rh_detalhe_full.json" -Encoding utf8
Write-Host "Total exported rows:" $rows.Count
"""

res = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
