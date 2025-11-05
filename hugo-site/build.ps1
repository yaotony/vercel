# Hugo 建置腳本
Write-Host "🔨 開始建置 Hugo 網站..." -ForegroundColor Green

# 檢查 Hugo 版本
Write-Host "Hugo 版本:" -ForegroundColor Yellow
hugo version

# 清理舊的建置
if (Test-Path "public") {
    Write-Host "🧹 清理舊的建置檔案..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "public"
}

# 執行建置
Write-Host "⚙️ 執行建置..." -ForegroundColor Yellow
hugo --gc --minify

# 檢查建置結果
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 建置成功完成！" -ForegroundColor Green
    
    # 顯示統計資訊
    $files = Get-ChildItem -Recurse "public" -File
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1KB
    
    Write-Host "📊 建置統計:" -ForegroundColor Cyan
    Write-Host "   檔案數量: $($files.Count)" -ForegroundColor White
    Write-Host "   總大小: $([math]::Round($totalSize, 2)) KB" -ForegroundColor White
    Write-Host "   輸出目錄: public/" -ForegroundColor White
} else {
    Write-Host "❌ 建置失敗！請檢查錯誤訊息。" -ForegroundColor Red
    exit 1
}