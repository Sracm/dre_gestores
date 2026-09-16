import subprocess
import time

t0 = time.time()

ps = r"""
[System.Reflection.Assembly]::LoadFrom('C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll') | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:63263;")
$conn.Open()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    DCALENDARIO[TRI ANO],
    VMQ_TSICUS[CODCENCUS],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    VW_MQ_TGFPAR_POWER_BI[NOME],
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$reader = $cmd.ExecuteReader()

$count = 0
while ($reader.Read()) {
    $count++
    if ($count % 100000 -eq 0) {
        Write-Host "Read $count rows..."
    }
}
$reader.Close()
$conn.Close()
Write-Host "Total rows read successfully: $count"
"""

res = subprocess.run(['powershell', '-Command', ps], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
print(f"Elapsed: {time.time() - t0:.2f}s")
