#!/bin/bash
set -euo pipefail
if [ "$#" -ne 1 ]; then echo 'Usage: bash Install-Mac.sh /path/to/brand'; exit 2; fi
package="$(cd "$(dirname "$0")" && pwd -P)"
source_dir="$package/template"
dest="$1"
case "$dest" in /*) ;; *) dest="$PWD/$dest" ;; esac
parent="$(dirname "$dest")"
if [ ! -d "$parent" ]; then echo '請先建立目的地的上層資料夾。'; exit 2; fi
dest="$(cd "$parent" && pwd -P)/$(basename "$dest")"
case "$dest/" in "$package/"*) echo '請選擇套件以外的私人資料夾。'; exit 2;; esac
if [ -L "$dest" ]; then echo '目的地不能是符號連結。'; exit 2; fi
if [ -e "$dest" ] && [ ! -d "$dest" ]; then echo '目的地不是資料夾。'; exit 2; fi
if [ -d "$dest" ]; then
 if [ -f "$dest/.kmw00-install.json" ]; then echo 'ALREADY_INSTALLED: 保留私人資料，不升級。'; exit 0; fi
 if [ -n "$(ls -A "$dest")" ]; then echo '目的地非空，未覆蓋任何檔案。'; exit 2; fi
fi
if [ -n "$(find "$source_dir" -type l -print -quit)" ]; then echo '來源不得含連結。'; exit 2; fi
count=0
while IFS= read -r line || [ -n "$line" ]; do
 hash="${line%%  *}"
 path="${line#*  }"
 if [ "${#hash}" -ne 64 ]; then echo '雜湊格式錯誤。'; exit 2; fi
 case "$hash" in *[!0-9a-f]*) echo '雜湊格式錯誤。';exit 2;;esac
 case "$path" in template/*) ;; *) echo '來源路徑錯誤。'; exit 2;; esac
 case "/$path/" in */../*|*/./*) echo '來源路徑錯誤。'; exit 2;; esac
 [ -f "$package/$path" ] || { echo '來源缺檔。'; exit 2; }
 count=$((count+1))
done < "$package/payload.sha256"
actual_count="$(find "$source_dir" -type f | wc -l | tr -d ' ')"
[ "$count" = "$actual_count" ] || { echo '來源清單不一致。'; exit 2; }
(cd "$package" && shasum -a 256 -c payload.sha256) >/dev/null
mkdir -p "$dest"
# Destination was checked empty; each file uses a fresh name, and a collision stops installation.
while IFS= read -r line || [ -n "$line" ]; do
 path="${line#*  }"
 relative="${path#template/}"
 target="$dest/$relative"
 mkdir -p "$(dirname "$target")"
 [ ! -e "$target" ] || { echo '安裝中發現衝突，停止。'; exit 2; }
 cp -p "$package/$path" "$target"
 cmp -s "$package/$path" "$target" || { echo '複製校驗失敗。'; exit 2; }
done < "$package/payload.sha256"
version="$(tr -d '\r\n' < "$package/VERSION")"
printf '{"package":"KMW00-brand-marketing","version":"%s","source":"https://github.com/DinoHappyKM/KMW00-brand-marketing"}\n' "$version" > "$dest/.kmw00-install.json"
echo "INSTALLED: $dest"
echo '請將此資料夾加入Codex並設為主要資料夾，再開始KMW00。'
