$env:HUGGINGFACE_API_KEY = (Get-Content .\.env | Where-Object {$_ -match '^HUGGINGFACE_API_KEY='} | ForEach-Object {$_ -replace '^HUGGINGFACE_API_KEY=',''} )
& 'C:\Users\dlali\Downloads\8fold\venv\Scripts\python.exe' 'c:\Users\dlali\Downloads\8fold\app.py' *> server.log
