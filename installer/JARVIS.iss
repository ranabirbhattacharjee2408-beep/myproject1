#define MyAppName "JARVIS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "JARVIS"
#define MyAppExeName "JARVIS.exe"
#define SourceDir ".."

[Setup]
AppId={{8F7E7D6A-6B4C-4E0D-9A11-JARVIS2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\JARVIS
DefaultGroupName=JARVIS

OutputDir=output
OutputBaseFilename=JARVIS_Setup

Compression=lzma
SolidCompression=yes

WizardStyle=modern

UninstallDisplayIcon={app}\JARVIS.exe

[Files]
Source: "{#SourceDir}\dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\JARVIS.exe"
Name: "{commondesktop}\JARVIS"; Filename: "{app}\JARVIS.exe"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch JARVIS"; Flags: nowait postinstall skipifsilent