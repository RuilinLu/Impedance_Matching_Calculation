; Impedance Matching AI v4.4.0 — Inno Setup 6 installer
; Build:  "C:\Users\Lenovo\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\ImpedanceMatchingAI.iss

#define MyAppName "Impedance Matching AI"
#define MyAppVersion "4.4.0"
#define MyAppPublisher "Impedance Matching AI contributors"
#define MyAppURL "https://github.com/SkywalkerHolmes/Impedance_Matching_Calculation"
#define MyAppExeName "ImpedanceMatchingAI.exe"
#define MyAppMcpExeName "ImpedanceMatchingAI_MCP.exe"
#define MyAppId "{{D3A6C1E1-6B25-4E55-9A3F-5C2B8D7E4F10}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\Impedance Matching AI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
InfoBeforeFile=README.txt
OutputDir=..\release
OutputBaseFilename=Impedance_Matching_AI_v{#MyAppVersion}_Setup
SetupIconFile=..\release\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
VersionInfoVersion=4.4.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce
Name: "uninstallicon"; Description: "创建“一键卸载”桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce

[Files]
Source: "..\release\Impedance_Matching_AI_v{#MyAppVersion}_Portable.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
Source: "..\release\Impedance_Matching_AI_v{#MyAppVersion}_MCP.exe"; DestDir: "{app}"; DestName: "{#MyAppMcpExeName}"; Flags: ignoreversion
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\SECURITY.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "TextBook_README.txt"; DestDir: "{app}\TextBook"; DestName: "README.txt"; Flags: ignoreversion
Source: "vendor\MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "vendor\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Dirs]
Name: "{app}\TextBook"; Permissions: users-modify
Name: "{app}\docs"; Permissions: users-modify
Name: "{localappdata}\ImpedanceMatchingAI"; Permissions: users-modify
Name: "{localappdata}\ImpedanceMatchingAI\TextBook"; Permissions: users-modify
Name: "{localappdata}\ImpedanceMatchingAI\data\library\books"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\离线说明书"; Filename: "{app}\docs\index.html"
Name: "{group}\教材库与数据库说明"; Filename: "{app}\docs\教材库说明.html"
Name: "{group}\MCP 配置说明"; Filename: "{app}\docs\mcp.zh.html"
Name: "{group}\一键卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autodesktop}\一键卸载 {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: uninstallicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletekey

[Run]
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "正在安装 Microsoft VC++ 运行库…"; Flags: waituntilterminated; Check: NeedsVCRedist
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; StatusMsg: "正在安装 Microsoft Edge WebView2 Runtime…"; Flags: waituntilterminated; Check: NeedsWebView2
Filename: "{app}\{#MyAppExeName}"; Parameters: "--init-data"; StatusMsg: "正在创建教材数据库…"; Flags: runhidden waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /T /IM {#MyAppExeName}"; Flags: runhidden waituntilterminated; RunOnceId: "KillGui"
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM {#MyAppMcpExeName}"; Flags: runhidden waituntilterminated; RunOnceId: "KillMcp"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\docs"
Type: filesandordirs; Name: "{app}\TextBook"

[Code]
var
  KeepUserData: Boolean;

procedure KillProcesses;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'),
    '/F /T /IM {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'),
    '/F /IM {#MyAppMcpExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure RunCleanup(DeleteData: Boolean);
var
  Params: String;
  ResultCode: Integer;
begin
  if DeleteData then
    Params := '--cleanup --app-dir "' + ExpandConstant('{app}') +
      '" --delete-user-data'
  else
    Params := '--cleanup --app-dir "' + ExpandConstant('{app}') +
      '" --keep-user-data --preserve-textbook';
  Log('Cleanup parameters: ' + Params);
  if not Exec(ExpandConstant('{app}\{#MyAppExeName}'), Params, '',
      SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Log('Cleanup could not be started')
  else
    Log('Cleanup exit code: ' + IntToStr(ResultCode));
end;

function InitializeUninstall(): Boolean;
var
  Answer: Integer;
  Tail: String;
  SilentMode: Boolean;
begin
  Result := True;
  Tail := LowerCase(GetCmdTail);
  SilentMode := UninstallSilent
    or (Pos('/verysilent', Tail) > 0)
    or (Pos('/silent', Tail) > 0);
  if Pos('/deletedata', Tail) > 0 then
    KeepUserData := False
  else if Pos('/keepdata', Tail) > 0 then
    KeepUserData := True
  else if SilentMode then
    KeepUserData := True
  else
  begin
    Answer := SuppressibleMsgBox(
      '是否保留个人数据与设置？' + #13#10 + #13#10 +
      '是：保留 API Key、界面设置、教材索引、上传/报告、翻译缓存和教材搜索路径，' +
      '下次安装可直接复用原来的使用习惯。' + #13#10 + #13#10 +
      '否：彻底删除本机保存的全部个人数据（不可恢复），并删除程序目录 TextBook。' + #13#10 + #13#10 +
      '自定义的教材搜索目录不会被卸载程序删除；选择“是”时程序目录 TextBook 会先复制到用户数据目录。',
      mbConfirmation, MB_YESNO, IDYES);
    KeepUserData := (Answer = IDYES);
  end;
  Log('Uninstall: keep user data = ' + IntToStr(Ord(KeepUserData)));
  KillProcesses;
  RunCleanup(not KeepUserData);
end;

function NeedsVCRedist: Boolean;
var
  Installed: Cardinal;
begin
  Result := True;
  if RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) then
    Result := Installed <> 1;
end;

function NeedsWebView2: Boolean;
var
  Version: String;
begin
  Result := True;
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) then
    Result := False;
  if RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) then
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    ForceDirectories(ExpandConstant('{localappdata}\ImpedanceMatchingAI\TextBook'));
    ForceDirectories(ExpandConstant('{localappdata}\ImpedanceMatchingAI\data\library\books'));
    SaveStringToFile(ExpandConstant('{localappdata}\ImpedanceMatchingAI\TextBook\README.txt'),
      'Place textbooks here (PDF, DOCX, PPTX, XLSX, TXT, Markdown).' + #13#10 +
      'The application indexes them locally; files are never uploaded.' + #13#10,
      False);
  end;
end;
