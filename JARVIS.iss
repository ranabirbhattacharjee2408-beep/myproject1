#define MyAppName "JARVIS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "JARVIS"
#define MyAppExeName "JARVIS.exe"
#define SourceDir ".."

[Setup]
AppId={{7C2B6F1E-4D5A-4B7E-9C3A-2F8E1D6A9B40}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\JARVIS
DefaultGroupName=JARVIS
OutputDir=output
OutputBaseFilename=JARVIS_Setup
SetupIconFile={#SourceDir}\JARVIS.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
Name: "startup"; Description: "Launch JARVIS automatically when Windows starts"

[Files]
Source: "{#SourceDir}\dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\JARVIS"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Checked by default above; "uninsdeletevalue" removes this automatically
; when JARVIS is uninstalled, so it never lingers in the registry.
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "JARVIS"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch JARVIS"; Flags: nowait postinstall skipifsilent
