$paths = @(
    ".\sql\mysql",
    ".\sql\postgress",
    ".\nosql\mongodb",
    ".\nosql\cassandra"
)

foreach ($path in $paths) {
    Write-Host "Uruchamiam: $path"
    Push-Location $path
    docker-compose up -d --build
    Pop-Location
}
