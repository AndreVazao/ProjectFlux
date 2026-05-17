[Setup]
AppName=ProjectFlux
AppVersion=1.0
DefaultDirName={pf}\ProjectFlux
DefaultGroupName=ProjectFlux
OutputDir=dist
OutputBaseFilename=ProjectFlux_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "flux\windows_service.py"; DestDir: "{app}\flux"

[Icons]
Name: "{group}\ProjectFlux"; Filename: "{app}\launcher.exe"
Name: "{commondesktop}\ProjectFlux"; Filename: "{app}\launcher.exe"

[Run]
; Install and start Windows Service (requires Admin)
Filename: "cmd.exe"; Parameters: "/c python {app}\flux\windows_service.py install"; Flags: runhidden

Filename: "cmd.exe"; Parameters: "/c python {app}\flux\windows_service.py start"; Flags: runhidden

Filename: "{app}\launcher.exe"; Description: "Launch ProjectFlux Cockpit"; Flags: nowait postinstall skipifsilent
