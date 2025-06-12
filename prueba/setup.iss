; Script generado por Inno Setup
     [Setup]
     AppName=Aplicación de Control ESP32
     AppVersion=1.0
     AppPublisher=Tu Nombre o Empresa
     DefaultDirName={autopf}\ESP32ControlApp
     DefaultGroupName=Aplicación de Control ESP32
     OutputBaseFilename=setup
     Compression=lzma
     SolidCompression=yes
     WizardStyle=modern

     [Files]
     Source: "dist\ESP32ControlApp.exe"; DestDir: "{app}"; Flags: ignoreversion
     Source: "mqtt_config.json"; DestDir: "{app}"; Flags: ignoreversion

     [Icons]
     Name: "{group}\Aplicación de Control ESP32"; Filename: "{app}\ESP32ControlApp.exe"
     Name: "{group}\{cm:UninstallProgram,Aplicación de Control ESP32}"; Filename: "{uninstallexe}"
     Name: "{autodesktop}\Aplicación de Control ESP32"; Filename: "{app}\ESP32ControlApp.exe"; Tasks: desktopicon

     [Tasks]
     Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

     [Run]
     Filename: "{app}\ESP32ControlApp.exe"; Description: "{cm:LaunchProgram,Aplicación de Control ESP32}"; Flags: nowait postinstall skipifsilent