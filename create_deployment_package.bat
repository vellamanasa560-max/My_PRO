@echo off
echo Creating deployment package...
powershell "Compress-Archive -Path 'app.py', 'requirements.txt', 'Procfile', 'pyproject.toml', 'render.yaml', 'templates', 'README.md' -DestinationPath 'chatbot-deployment.zip' -Force"
echo.
echo Deployment package created: chatbot-deployment.zip
echo.
echo Next steps:
echo 1. Go to your GitHub repository
echo 2. Click "Add file" -^> "Upload files"
echo 3. Upload the chatbot-deployment.zip file
echo 4. Extract/unzip the files in GitHub
echo 5. Connect your GitHub repo to Render
echo.
pause