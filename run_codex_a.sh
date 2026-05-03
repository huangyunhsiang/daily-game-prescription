#!/bin/bash
cd /mnt/c/Al-Agent-workspace/daily-game-prescription
/home/kasper-ai/.npm-global/bin/codex exec --sandbox workspace-write "$(cat /tmp/codex_task_a.txt)"
