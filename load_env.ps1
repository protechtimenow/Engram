# Load Environment Variables from .env file
# Usage: . .\load_env.ps1

$envFile = ".env"

if (-Not (Test-Path $envFile)) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Loading environment variables from $envFile..." -ForegroundColor Cyan

$lineCount = 0
$loadedCount = 0
$skippedCount = 0

Get-Content $envFile | ForEach-Object {
    $lineCount++
    $line = $_.Trim()
    
    # Skip empty lines and comments
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
        $skippedCount++
        return
    }
    
    # Parse KEY=VALUE format
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Skip if key or value is empty
        if ([string]::IsNullOrWhiteSpace($key)) {
            Write-Host "⚠️  Line $lineCount: Skipping empty key" -ForegroundColor Yellow
            $skippedCount++
            return
        }
        
        # Set environment variable
        try {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            $loadedCount++
            Write-Host "✅ $key = $value" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to set $key : $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "⚠️  Line $lineCount: Invalid format (expected KEY=VALUE): $line" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "   Total lines: $lineCount" -ForegroundColor White
Write-Host "   Loaded: $loadedCount" -ForegroundColor Green
Write-Host "   Skipped: $skippedCount" -ForegroundColor Yellow
Write-Host "`n✅ Environment variables loaded successfully!" -ForegroundColor Green
