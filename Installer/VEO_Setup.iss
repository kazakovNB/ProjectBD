; VEO installer (Inno Setup)
; Build outputs expected:
;   - Server\dist\VEOServer\VEOServer.exe
;   - Server\dist\VEO_DB_Setup\VEO_DB_Setup.exe
;   - VEOClient\dist\VEOClient\VEOClient.exe

#define MyAppName "VEO"
#define MyAppPublisher "VEO Development Team"
#define MyAppVersion "1.0"
#define MyAppExeName "VEOClient.exe"

[Setup]
AppId={{8F7B2A7F-2E0D-4A4C-9F7D-9A0A1E8F4A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=VEO_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\InstallerAssets\veo_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать значок на рабочем столе"; GroupDescription: "Дополнительно:"; Flags: unchecked

[Dirs]
Name: "{commonappdata}\VEO"; Permissions: users-modify
Name: "{commonappdata}\VEO\videos"; Permissions: users-modify

[Files]
; Client
Source: "..\VEOClient\dist\VEOClient\*"; DestDir: "{app}\Client"; Flags: recursesubdirs ignoreversion

; Server
Source: "..\Server\dist\VEOServer\*"; DestDir: "{app}\Server"; Flags: recursesubdirs ignoreversion
Source: "..\Server\dist\VEO_DB_Setup\*"; DestDir: "{app}\DBSetup"; Flags: recursesubdirs ignoreversion

; Docs
Source: "..\Docs\USER_GUIDE.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion
Source: "..\Docs\VEO_User_Guide_Windows.pdf"; DestDir: "{app}\Docs"; Flags: ignoreversion

[Icons]
Name: "{group}\VEO Client"; Filename: "{app}\Client\VEOClient.exe"; WorkingDir: "{app}\Client"
Name: "{group}\VEO Server"; Filename: "{app}\Server\VEOServer.exe"; WorkingDir: "{app}\Server"
Name: "{group}\VEO Database Setup"; Filename: "{app}\DBSetup\VEO_DB_Setup.exe"; WorkingDir: "{app}\DBSetup"
Name: "{group}\Документация"; Filename: "{app}\Docs\VEO_User_Guide_Windows.pdf"; WorkingDir: "{app}\Docs"
Name: "{commondesktop}\VEO Client"; Filename: "{app}\Client\VEOClient.exe"; Tasks: desktopicon

[Run]
; Offer to run DB setup after install
Filename: "{app}\DBSetup\VEO_DB_Setup.exe"; Description: "Запустить настройку базы данных (рекомендуется)"; Flags: postinstall nowait skipifsilent

