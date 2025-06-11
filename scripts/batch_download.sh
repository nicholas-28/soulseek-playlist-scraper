#!/bin/bash

# Batch download for all playlists

cd "$(dirname "$0")/.."  # Go to project root

for txtfile in playlists/*.txt; do
  playlist=$(basename "$txtfile" .txt)
  mkdir -p "downloads/$playlist"
  while IFS= read -r track; do
    soulseek download "$track" --quality=320 --destination="downloads/$playlist"
  done < "$txtfile"
done
