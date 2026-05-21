[Setup]
AppName=AutoTrack
AppVersion=2.0
DefaultDirName={pf}\AutoTrack
DefaultGroupName=AutoTrack
OutputDir=Output
OutputBaseFilename=AutoTrack_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные значки:"

[Files]
; ВНИМАНИЕ: Убедитесь, что путь к папке dist\AutoTrack указан верно
Source: "dist\AutoTrack\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AutoTrack"; Filename: "{app}\AutoTrack.exe"
Name: "{commondesktop}\AutoTrack"; Filename: "{app}\AutoTrack.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AutoTrack.exe"; Description: "Запустить AutoTrack"; Flags: nowait postinstall skipifsilent
