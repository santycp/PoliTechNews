# Exporta únicamente el informe de esta entrega y actualiza sus campos de Word.
$ErrorActionPreference='Stop'
$workspacePath=Split-Path $PSScriptRoot -Parent
$documentPath=Join-Path $workspacePath 'output/docx/PoliTechNews_Entrega_3.docx'
$pdfPath=Join-Path $workspacePath 'output/pdf/PoliTechNews_Entrega_3.pdf'
$wordInstance=$null
$documentInstance=$null
try {
  $wordInstance=New-Object -ComObject Word.Application
  $wordInstance.Visible=$false
  $wordInstance.DisplayAlerts=0
  $documentInstance=$wordInstance.Documents.Open($documentPath)
  foreach ($toc in $documentInstance.TablesOfContents) { $toc.Update() }
  $documentInstance.Fields.Update() | Out-Null
  $documentInstance.Repaginate()
  foreach ($toc in $documentInstance.TablesOfContents) { $toc.Update() }
  $documentInstance.Save()
  $documentInstance.ExportAsFixedFormat($pdfPath,17)
  Write-Output "WORD_PDF_OK pages=$($documentInstance.ComputeStatistics(2))"
} finally {
  if ($documentInstance) { $documentInstance.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($documentInstance) }
  if ($wordInstance) { $wordInstance.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordInstance) }
}
