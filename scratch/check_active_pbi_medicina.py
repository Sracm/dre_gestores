import subprocess

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
    VMQ_TSIEMP[RAZAOABREV],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    VW_MQ_TGFPAR_POWER_BI[NOME],
    FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] = 9010000),
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NUMEROMES] = 9),
    FILTER(VMQ_TGFNAT, SEARCH("MEDICINA", VMQ_TGFNAT[DESCRNAT], 1, 0) > 0),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$lines = @()
foreach ($r in $dt.Rows) {
    $lines += "Empresa: $($r['VMQ_TSIEMP[RAZAOABREV]']) | Parc: $($r['VW_MQ_TGFPAR_POWER_BI[NOME]']) | Orc: $($r['[ORCADO]']) | Real: $($r['[REALIZADO]'])"
}

$conn.Close()
$lines | Out-File -FilePath "$PWD/scratch/active_medicina.txt" -Encoding utf8
"""

subprocess.run(['powershell', '-Command', ps_script])

with open('scratch/active_medicina.txt', 'r', encoding='utf-8') as f:
    print(f.read())
