; Inno Setup Script
; Đóng gói ứng dụng 'Tra cứu hồ sơ Bản vẽ PDF' thành bộ cài đặt Setup_TraCuuBanVePDF_v1.0.exe
; Hỗ trợ Windows 7, 8, 10, 11 (32-bit & 64-bit)

#define MyAppName "Tra cứu hồ sơ PDF"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CAD / PDF Engineering Tools"
#define MyAppExeName "TraCuuBanVePDF.exe"
#define MyAppAssocName "Hồ sơ Bản vẽ PDF"

[Setup]
AppId={{5E9A8E89-B0F3-46B4-9F81-9C3E3A4D0F82}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=setup_output
OutputBaseFilename=Setup_TraCuuBanVePDF_v1.0
SetupIconFile=logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Khởi động cùng Windows (chạy ngầm, gọi nhanh bằng Shift Shift)"; GroupDescription: "Tự động kích hoạt:"

; =====================================================================
; [FILES] CÁC FILE ĐƯỢC ĐÓNG GÓI VÀO BỘ CÀI ĐẶT
; LƯU Ý: Trước khi bấm "Compile" (F9) trong Inno Setup:
; Bạn BẮT BUỘC phải chạy file "build_installer.bat" (hoặc lệnh "python build_exe.py")
; để PyInstaller tạo ra thư mục "dist\TraCuuBanVePDF\" trước!
; =====================================================================
[Files]
Source: "dist\TraCuuBanVePDF\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "Huong_Dan_Cai_Dat.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
