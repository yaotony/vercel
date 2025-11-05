# 快速啟動 Hugo 開發伺服器
Write-Host "🚀 啟動 Hugo 開發伺服器..." -ForegroundColor Green
Write-Host "🌐 網址: http://localhost:1313" -ForegroundColor Cyan
Write-Host "📝 包含草稿和未來文章" -ForegroundColor Yellow
Write-Host "⚡ 按 Ctrl+C 停止伺服器" -ForegroundColor Red

hugo server --bind=0.0.0.0 --port=1313 --buildDrafts --buildFuture --disableFastRender