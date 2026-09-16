import subprocess

ps = r"""
[System.Reflection.Assembly]::LoadFrom('C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll') | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:63263;")
$conn.Open()

$dax = @"
EVALUATE
ROW(
    "TotalRowsFSP",
    COUNTROWS(
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
            FILTER(VMQ_TSICUS, VMQ_TSICUS[CODCENCUS] IN {1020000, 1010200, 1010300, 1010400, 9010000}),
            "ORCADO", [ORÇADO (R$).],
            "REALIZADO", [REALIZADO (R$)..]
        )
    ),
    "TotalRowsAll",
    COUNTROWS(
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
    )
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

Write-Host "TotalRowsFSP:" $dt.Rows[0]["[TotalRowsFSP]"]
Write-Host "TotalRowsAll:" $dt.Rows[0]["[TotalRowsAll]"]
$conn.Close()
"""

res = subprocess.run(['powershell', '-Command', ps], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
