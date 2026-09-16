# Registra no Agendador de Tarefas do Windows a atualização do DRE a cada 30 minutos.
# Executar no servidor que roda o app.py, em um PowerShell como administrador:
#   powershell -ExecutionPolicy Bypass -File etl\agendar_tarefa.ps1
# Para remover:
#   Unregister-ScheduledTask -TaskName "DRE Gestores - Atualizar dados" -Confirm:$false

param(
    [int]$IntervaloMinutos = 30,
    [string]$Python = (Get-Command python).Source
)

$projeto = Split-Path -Parent $PSScriptRoot
$nome = "DRE Gestores - Atualizar dados"

$acao = New-ScheduledTaskAction -Execute $Python -Argument "-m etl.atualizar_dados" -WorkingDirectory $projeto
$gatilho = New-ScheduledTaskTrigger -Daily -At 21:00
$config = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho -Settings $config `
    -Description "Extrai VMQ_DREQLIK do Oracle e atualiza o dre_cache.db (etl\atualizar_dados.py)" `
    -RunLevel Highest -Force | Out-Null

Write-Host "Tarefa '$nome' registrada: Diariamente às 21:00, usando $Python em $projeto"
