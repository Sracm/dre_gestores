import subprocess

ps = """
[System.Reflection.Assembly]::LoadFrom("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:58493;")
$conn.Open()

# Test 1: With Report & Page Filters
$dax1 = @"
EVALUATE
SUMMARIZECOLUMNS(
    VMQ_CADDRE[BLOCO],
    VMQ_CADDRE[TITULO],
    FILTER(DCALENDARIO, DCALENDARIO[ANO] = 2026 && DCALENDARIO[NOMEMES] = "mar"),
    FILTER(VMQ_CADDRE, VMQ_CADDRE[BLOCO] IN {"1.Venda Liquida", "3.Despesas com Vendas", "4.Despesas Comercial Operacional", "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras"}),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[CODEMP] <> 9),
    FILTER(VMQ_TSIEMP, NOT(VMQ_TSIEMP[RAZAOABREV] IN {"EA88 - SC", "EKOS - SP", "GLOBRAL - SC", "GLOBRAL - SP", "AGGP - SP"})),
    FILTER(VMQ_DREQLIK, VMQ_DREQLIK[CODCENCUS] <> 21010000),
    FILTER(VMQ_TSIEMP, VMQ_TSIEMP[RAZAOABREV] IN {"Consolidação", "FORX", "MCR - FABRICA", "MCR - FILIAL 03", "MCR - MATRIZ", "MCR - SC", "QUALITY - RJ", "QUALITY MATRIZ", "SL ONLINE - SP", "VLS - RJ", "VLS - SP", "FORX MG"}),
    "REALIZADO", [REALIZADO (R$)..],
    "ORCADO", [ORÇADO (R$).]
)
ORDER BY VMQ_CADDRE[BLOCO], VMQ_CADDRE[TITULO]
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax1
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$dt = New-Object System.Data.DataTable
$adapter.Fill($dt) | Out-Null

$list = @()
foreach ($r in $dt.Rows) {
    $list += [PSCustomObject]@{
        BLOCO = $r["VMQ_CADDRE[BLOCO]"]
        TITULO = $r["VMQ_CADDRE[TITULO]"]
        REALIZADO = [Math]::Round([double]$r["[REALIZADO]"], 2)
        ORCADO = [Math]::Round([double]$r["[ORCADO]"], 2)
    }
}
$list | ConvertTo-Json | Out-File -FilePath "dax_test1_result.json" -Encoding utf8

$conn.Close()
Write-Host "Test 1 done!"
"""

with open("test_filters.ps1", "w", encoding="utf-8-sig") as f:
    f.write(ps)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "test_filters.ps1"], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("ERR:", res.stderr)
