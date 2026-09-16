import subprocess

ps_content = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:64795;")
$conn.Open()

Write-Host "Executing aggregated export for DRE Gestores..."
$sw = [System.Diagnostics.Stopwatch]::StartNew()

$dax = @"
EVALUATE
SUMMARIZECOLUMNS(
    DCALENDARIO[ANO],
    DCALENDARIO[NUMEROMES],
    DCALENDARIO[NOMEMES],
    DCALENDARIO[TRIMESTRE],
    DCALENDARIO[TRI ANO],
    DCALENDARIO[SEM],
    VMQ_TSIEMP[RAZAOABREV],
    VMQ_TSICUS[CODCENCUS],
    VMQ_TSICUS[DESCRCENCUS],
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    VMQ_TGFNAT[DESCRNAT],
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    "ORCADO", [ORÇADO (R$).],
    "REALIZADO", [REALIZADO (R$)..],
    "VB_ORCADO", [VENDA BRUTA ORCADO],
    "VB_REALIZADO", [VENDA BRUTA REALIZADO]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null
$sw.Stop()

Write-Host "Exported $($dt.Rows.Count) rows in $($sw.ElapsedMilliseconds) ms!"

$csvPath = "$PWD\\dre_cube_data.csv"
$writer = [System.IO.StreamWriter]::new($csvPath, $false, [System.Text.Encoding]::UTF8)

# Header
$cols = @($dt.Columns | ForEach-Object { $_.ColumnName })
$writer.WriteLine(($cols -join "`t"))

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
Write-Host "Saved dre_cube_data.csv ($([Math]::Round((Get-Item $csvPath).Length / 1MB, 2)) MB)"

$conn.Close()
"""

with open("export_dre_cube.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps_content)

print("Saved export_dre_cube.ps1 with utf-8-sig")
