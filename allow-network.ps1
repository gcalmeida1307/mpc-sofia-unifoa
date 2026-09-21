$ErrorActionPreference = 'Stop'

# Execute este arquivo em um PowerShell aberto como Administrador.
# As regras ficam restritas ao perfil Private da rede interna.
$rules = @(
  @{ Name = 'S.O.F.I.A. Local UI 5174'; Port = 5174 },
  @{ Name = 'S.O.F.I.A. Local API 8787'; Port = 8787 }
)

foreach ($rule in $rules) {
  $existing = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
  if (-not $existing) {
    New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Action Allow -Protocol TCP -LocalPort $rule.Port -Profile Private -Description 'Acesso da plataforma SOFIA na rede interna'
  } else {
    Set-NetFirewallRule -DisplayName $rule.Name -Enabled True -Direction Inbound -Action Allow -Profile Private
  }
}

Write-Host 'Portas 5174 e 8787 liberadas somente no perfil Private.'
