# install.ps1

# Check if pip is installed
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
  Write-Host "pip is not installed. Please install Python and pip first." -ForegroundColor Red
  exit 1
}

# Define the required packages - NEEDS TO BE UPDATED
$packages = @(
  "discord",
  "discord-py-interactions",
  "python-decouple",
  "requests"
)

# Install each package
foreach ($package in $packages) {
  Write-Host "Installing $package..."
  pip install $package
}

Write-Host "All packages installed successfully." -ForegroundColor Green