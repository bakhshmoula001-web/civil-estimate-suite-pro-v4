#define MyAppName "Civil Estimate Suite Pro"
#define MyAppVersion "4.0.0"
#define MyAppPublisher "Civil Estimate Suite Pro"
#define MyAppExeName "Civil Estimate Suite Pro 4.0.exe"

[Setup]
AppId={{8D6B8E3A-4F0D-4B65-9A40-CIVILESTIMATE40}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Civil Estimate Suite Pro 4.0
DefaultGroupName=Civil Estimate Suite Pro 4.0

OutputDir=installer
OutputBaseFilename=Civil_Estimate_Suite_Pro_4.0_Setup

Compression=lzma
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\Civil Estimate Suite Pro 4.0\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Civil Estimate Suite Pro 4.0"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Civil Estimate Suite Pro 4.0"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Civil Estimate Suite Pro 4.0"; Flags: nowait postinstall skipifsilent