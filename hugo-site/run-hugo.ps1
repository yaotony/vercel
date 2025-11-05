# Hugo 執行腳本 - 開發模式
# 使用方法: .\run-hugo.ps1 [build|dev|clean|deploy]

param(
    [string]$Action = "dev"
)

# 設定顏色輸出
function Write-ColorText {
    param([string]$Text, [string]$Color = "Green")
    Write-Host $Text -ForegroundColor $Color
}

# 確保在正確的目錄中
Set-Location -Path $PSScriptRoot

Write-ColorText "🚀 Hugo 執行腳本" "Cyan"
Write-ColorText "當前目錄: $(Get-Location)" "Yellow"
Write-ColorText "執行動作: $Action" "Yellow"

switch ($Action.ToLower()) {
    "dev" {
        Write-ColorText "📝 啟動開發伺服器..." "Green"
        hugo server --bind=0.0.0.0 --port=1313 --buildDrafts --buildFuture --disableFastRender
    }
    
    "build" {
        Write-ColorText "🔨 建置網站..." "Green"
        hugo --gc --minify
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ 建置完成！輸出目錄: public/" "Green"
        } else {
            Write-ColorText "❌ 建置失敗！" "Red"
        }
    }
    
    "clean" {
        Write-ColorText "🧹 清理快取和輸出..." "Green"
        if (Test-Path "public") {
            Remove-Item -Recurse -Force "public"
            Write-ColorText "已刪除 public 目錄" "Yellow"
        }
        if (Test-Path "resources") {
            Remove-Item -Recurse -Force "resources"
            Write-ColorText "已刪除 resources 目錄" "Yellow"
        }
        hugo --gc
        Write-ColorText "✅ 清理完成！" "Green"
    }
    
    "deploy" {
        Write-ColorText "🚀 部署模式建置..." "Green"
        # 先清理
        if (Test-Path "public") {
            Remove-Item -Recurse -Force "public"
        }
        
        # 建置
        hugo --gc --minify
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ 部署建置完成！" "Green"
            Write-ColorText "📁 輸出目錄: public/" "Cyan"
            
            # 顯示檔案大小統計
            $publicSize = (Get-ChildItem -Recurse "public" | Measure-Object -Property Length -Sum).Sum / 1MB
            Write-ColorText "📊 輸出大小: $([math]::Round($publicSize, 2)) MB" "Yellow"
        } else {
            Write-ColorText "❌ 部署建置失敗！" "Red"
        }
    }
    
    "preview" {
        Write-ColorText "👀 預覽建置結果..." "Green"
        hugo server --source=public --bind=0.0.0.0 --port=8080 --navigateToChanged=false
    }
    
    default {
        Write-ColorText "❓ 未知的動作: $Action" "Red"
        Write-ColorText "可用的動作:" "Yellow"
        Write-ColorText "  dev     - 啟動開發伺服器" "White"
        Write-ColorText "  build   - 建置網站" "White"
        Write-ColorText "  clean   - 清理快取和輸出" "White"
        Write-ColorText "  deploy  - 部署模式建置" "White"
        Write-ColorText "  preview - 預覽建置結果" "White"
    }
}