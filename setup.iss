; اسکریپت نصب‌کننده ArchivePro با پشتیبانی از Repair/Uninstall
[Setup]
AppId={{ArchivePro-2025-GUID-001}
AppName=ArchivePro
AppVersion=1.0
AppVerName=ArchivePro 1.0
AppPublisher=Majid Dehaki
DefaultDirName={autopf}\ArchivePro
DefaultGroupName=ArchivePro
UninstallDisplayIcon={app}\main.exe
SetupIconFile=ArchivePro.ico
Compression=lzma2
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=ArchivePro_Setup
DisableDirPage=auto
DisableProgramGroupPage=auto
UsePreviousAppDir=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\ArchivePro"; Filename: "{app}\main.exe"; IconFilename: "{app}\main.exe"
Name: "{commondesktop}\ArchivePro"; Filename: "{app}\main.exe"; IconFilename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Run ArchivePro"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"