# PowerShell script to package the project for GitHub

# Define the project directory
$ProjectDir = "c:\Users\John\Desktop\FFC\groqeeAHK2"

# Define the target directory for packaging
$TargetDir = "$ProjectDir\GitHubPackage"

# Remove the target directory if it exists
if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}

# Create the target directory
New-Item -ItemType Directory -Path $TargetDir

# Copy necessary files and folders to the target directory
Copy-Item -Path "$ProjectDir\VoiceInteractiveAssistant" -Destination "$TargetDir" -Recurse -Exclude __pycache__,*.wav,temp_audio,groq_api_key.txt,memory.json,user_profile.json

# Create a zip file for the package
$ZipFile = "$ProjectDir\GroqeeVFJD_Package.zip"
if (Test-Path $ZipFile) {
    Remove-Item -Force $ZipFile
}
Compress-Archive -Path $TargetDir\* -DestinationPath $ZipFile

# Clean up the temporary package directory
Remove-Item -Recurse -Force $TargetDir

Write-Host "Project packaged successfully as $ZipFile"