param([ValidateSet('status','enable','runs')][string]$Action='status')
$ErrorActionPreference='Stop'
$apiBase='https://api.github.com/repos/santycp/PoliTechNews'
# Usa la credencial guardada por Git solo en memoria. Nunca imprime ni guarda el token.
$credentialOutput="protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
if ($LASTEXITCODE -ne 0) { throw 'No hay una credencial GitHub disponible para configurar Pages.' }
$credentialData=@{}
foreach ($line in $credentialOutput) { if ($line -match '^([^=]+)=(.*)$') { $credentialData[$Matches[1]]=$Matches[2] } }
if (!$credentialData['password']) { throw 'La credencial GitHub no contiene un token utilizable.' }
$headers=@{ Authorization="Bearer $($credentialData['password'])"; Accept='application/vnd.github+json'; 'X-GitHub-Api-Version'='2022-11-28'; 'User-Agent'='PoliTechNews-entrega3' }
try {
  if ($Action -eq 'runs') {
    $result=Invoke-RestMethod -Uri "$apiBase/actions/workflows/pages.yml/runs?per_page=3" -Headers $headers
    $result.workflow_runs | Select-Object id,status,conclusion,html_url,head_sha | ConvertTo-Json -Depth 3
  } else {
    $pages=$null
    try { $pages=Invoke-RestMethod -Uri "$apiBase/pages" -Headers $headers }
    catch { if ([int]$_.Exception.Response.StatusCode -ne 404) { throw } }
    if ($Action -eq 'enable') {
      if ($pages) { $pages=Invoke-RestMethod -Uri "$apiBase/pages" -Method Put -Headers $headers -ContentType 'application/json' -Body '{"build_type":"workflow"}' }
      else { $pages=Invoke-RestMethod -Uri "$apiBase/pages" -Method Post -Headers $headers -ContentType 'application/json' -Body '{"build_type":"workflow"}' }
      if (!$pages) { $pages=Invoke-RestMethod -Uri "$apiBase/pages" -Headers $headers }
    }
    if ($pages) { $pages | Select-Object status,html_url,build_type,public | ConvertTo-Json }
    else { Write-Output 'PAGES_NOT_ENABLED' }
  }
} finally { $headers.Clear(); $credentialData.Clear(); $credentialOutput=$null }
