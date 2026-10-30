param([string]$Destination, [switch]$NonInteractive)
$ErrorActionPreference='Stop'
try {
 if([string]::IsNullOrWhiteSpace($Destination)){
  if($NonInteractive){throw '請提供完整目的地路徑。'}
  Write-Host 'KMW00 Windows 安裝。指定品牌資料夾本身就是根目錄。'
  Write-Host '建議選一般本機資料夾，例如 C:\KMW00\我的品牌。既有企劃保留、不重置。'
  $Destination=Read-Host '請貼上私人品牌資料夾完整路徑'
 }
 $Destination=$Destination.Trim().Trim('"')
 if(-not [IO.Path]::IsPathRooted($Destination)){throw '請輸入完整路徑，不使用相對路徑。'}
 $dest=[IO.Path]::GetFullPath($Destination)
 # This starts the same reviewed installer in a normal user PowerShell process.
 # Bypass applies only to this child process, never changes machine policy.
 $result=@(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'Install-Windows.ps1') -Destination $dest 2>&1)
 $status=$LASTEXITCODE
 foreach($line in $result){Write-Host $line}
 if($status -ne 0){throw ('安裝器未完成，保留既有檔案。退出碼：'+$status)}
 $required=@('AGENTS.md','00_系統規則_System.md','01_品牌知識_Brand.md','02_專案狀態_Project.md','03_知識索引_Index.md')
 foreach($name in $required){if(-not(Test-Path -LiteralPath (Join-Path $dest $name) -PathType Leaf)){throw ('必要檔案缺失：'+$name+'；保留原資料，請檢查既有安裝。')}}
 Write-Host ('VERIFIED: '+$dest)
 Write-Host '下一步：將這個品牌資料夾單獨加入Codex。先確認能讀檔，再輸入開始KMW00。'
 if(-not $NonInteractive){[void](Read-Host '按Enter關閉')}
 exit 0
} catch {
 Write-Host ('未完成：'+$_.Exception.Message)
 if(-not $NonInteractive){[void](Read-Host '按Enter關閉')}
 exit 1
}
