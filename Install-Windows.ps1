param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
function File-Sha256([string]$Path) {
 $stream=[IO.File]::OpenRead($Path);$sha=[Security.Cryptography.SHA256]::Create()
 try {return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()} finally {$stream.Dispose();$sha.Dispose()}
}
$package=[IO.Path]::GetFullPath($PSScriptRoot)
$source=Join-Path $package 'template'
$dest=[IO.Path]::GetFullPath($Destination)
if($dest -eq $package -or $dest.StartsWith($package.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw '請選擇套件資料夾以外的私人品牌工作區。'}
$ancestor=$dest
while($ancestor){
 if(Test-Path -LiteralPath $ancestor){if((Get-Item -LiteralPath $ancestor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw '目的地含連結或重新解析點，請選一般本機資料夾。'}}
 $next=Split-Path -Parent $ancestor;if($next -eq $ancestor){break};$ancestor=$next
}
if(Test-Path -LiteralPath $dest){
 if(-not(Test-Path -LiteralPath $dest -PathType Container)){throw '目的地不是資料夾。'}
 if(Test-Path -LiteralPath (Join-Path $dest '.kmw00-install.json')){Write-Output 'ALREADY_INSTALLED: 保留全部私人資料；此操作不升級。';exit 0}
 if(@(Get-ChildItem -LiteralPath $dest -Force).Count -gt 0){throw '目的地非空，未覆蓋任何檔案。'}
}
$paths=@()
foreach($line in Get-Content -LiteralPath (Join-Path $package 'payload.sha256') -Encoding UTF8){
 if($line -notmatch '^([a-f0-9]{64})  (template/.+)$'){throw '套件雜湊清單格式不正確。'}
 $expected=$Matches[1];$relative=$Matches[2]
 $path=[IO.Path]::GetFullPath((Join-Path $package $relative))
 if(-not $path.StartsWith($source.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw '來源超出模板。'}
 if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "缺少來源：$relative"}
 if((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint){throw '來源不得含連結。'}
 if((File-Sha256 $path) -ne $expected){throw "來源校驗失敗：$relative"}
 if($paths -contains $path){throw '來源路徑重複。'};$paths+=$path
}
$sourceFiles=@(Get-ChildItem -LiteralPath $source -Recurse -Force -File)
if($paths.Count -ne $sourceFiles.Count){throw '來源有未列入清單的檔案。'}
if(@(Get-ChildItem -LiteralPath $source -Recurse -Force | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw '來源不得含連結。'}
New-Item -ItemType Directory -Path $dest -Force | Out-Null
foreach($path in $paths){
 $relative=$path.Substring($source.Length).TrimStart('\','/')
 $target=Join-Path $dest $relative
 New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
 if(Test-Path -LiteralPath $target){throw '安裝中目的地發生衝突，停止；請保留資料並另選空資料夾。'}
 [IO.File]::Copy($path,$target,$false)
 if((File-Sha256 $path) -ne (File-Sha256 $target)){throw '複製後校驗失敗。'}
}
$record=@{package='KMW00-brand-marketing';version=(Get-Content -LiteralPath (Join-Path $package 'VERSION') -Raw).Trim();source='https://github.com/DinoHappyKM/KMW00-brand-marketing';installed_at=(Get-Date).ToUniversalTime().ToString('o')}
[IO.File]::WriteAllText((Join-Path $dest '.kmw00-install.json'),($record|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
Write-Output "INSTALLED: $dest"
Write-Output '請將此資料夾加入Codex並設為主要資料夾，再開始KMW00。'