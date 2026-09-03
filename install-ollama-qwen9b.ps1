$ErrorActionPreference = 'Stop'

$model = 'hf.co/ge525/Qwen3.8-9B-Distill-uncensored-heretic-Q4_K_M-GGUF:Q4_K_M'
$minimumFreeBytes = 8GB
$freeBytes = (Get-PSDrive -Name C).Free

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  throw 'Ollama não foi encontrado no PATH. Instale o Ollama e execute este script novamente.'
}

if ($freeBytes -lt $minimumFreeBytes) {
  throw ('Espaço livre insuficiente em C:. São recomendados pelo menos 8 GB; disponíveis: {0:N2} GB.' -f ($freeBytes / 1GB))
}

Write-Host "Baixando o modelo local: $model"
ollama pull $model
Write-Host ''
Write-Host 'Modelo instalado. Para testar sem alterar a configuração da SOFIA:'
Write-Host "  ollama run $model"
Write-Host ''
Write-Host 'Para ativá-lo na SOFIA, defina no .env:'
Write-Host "  OLLAMA_MODEL=$model"
Write-Host 'Depois reinicie start-local.ps1.'
