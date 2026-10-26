; ============================================================================
; 智配芯生 · ImpedanceMCP v4.3.0 — Inno Setup 6 installer
; Build:  iscc /Qp installer\ImpedanceMCP.iss
; ============================================================================

#define MyAppName "智配芯生 · ImpedanceMCP"
#define MyAppVersion "4.3.0"
#define MyAppPublisher "Ruilin Lu, Keji Lu, Zhiyi Lin, Yunlei Zhang"
#define MyAppURL "https://github.com/RuilinLu/Impedance_Matching_Calculation"
#define MyAppExeName "ImpedanceMCP.exe"
#define MyAppMcpExeName "ImpedanceMCP_MCP.exe"
#define MyAppContact "radarlurui@gmail.com | Lu_Skywalker2915@sjtu.edu.cn"

[Setup]
AppId={{A4C1E2D3-5B6F-4A7E-9C8D-1E2F3A4B5C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppContact={#MyAppContact}
AppComments=独立运行软件 + MCP 服务器；微波阻抗匹配计算、Smith 圆图、扫描、耐压与报告。
DefaultDirName={autopf}\ImpedanceMCP
DefaultGroupName=智配芯生 ImpedanceMCP
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename=ImpedanceMCP_Setup_v{#MyAppVersion}
SetupIconFile=..\release\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}（一键卸载会清除全部数据）
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
UsePreviousTasks=yes
SetupLogging=yes
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany=Shanghai Jiao Tong University - School of Integrated Circuits
VersionInfoDescription=ImpedanceMCP installer - microwave impedance matching software and MCP server
VersionInfoCopyright=Copyright (c) 2025-2026 Ruilin Lu, Keji Lu, Zhiyi Lin, Yunlei Zhang. MIT License.
VersionInfoProductName=智配芯生 · ImpedanceMCP
VersionInfoProductVersion={#MyAppVersion}.0

[Languages]
Name: "chinesesimp"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce
Name: "startmenu"; Description: "创建开始菜单快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce
Name: "helpmenu"; Description: "创建帮助文档快捷方式（用户手册 / MCP 说明）"; GroupDescription: "快捷方式："; Flags: checkedonce
Name: "mcpzcode"; Description: "为 ZCode 写入 MCP 配置（自动备份原配置）"; GroupDescription: "MCP："; Flags: checkedonce
Name: "classic"; Description: "安装原版 MATLAB 经典界面（需要 MATLAB Runtime R2023b）"; GroupDescription: "可选组件："; Flags: checkedonce
Name: "uninstallicon"; Description: "创建桌面“一键卸载”快捷方式（会删除程序、数据和配置）"; GroupDescription: "快捷方式："; Flags: unchecked
Name: "launch"; Description: "安装完成后启动 ImpedanceMCP"; GroupDescription: "完成后："; Flags: checkedonce

[Files]
; --- one-folder application payload (native GUI + console MCP) ---
Source: "..\release\ImpedanceMCP_v4.3.0_App\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- built-in documentation (help center + PDF) ---
Source: "..\docs\*.html"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\*.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion

; --- project docs / license ---
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

; --- classic MATLAB GUI (optional) ---
Source: "vendor\classic\Impedance_Matching.exe"; DestDir: "{app}\classic"; Flags: ignoreversion skipifsourcedoesntexist; Tasks: classic
Source: "vendor\classic\readme.txt"; DestDir: "{app}\classic"; Flags: ignoreversion skipifsourcedoesntexist; Tasks: classic

; --- prerequisite installers (only run when missing) ---
Source: "vendor\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall skipifsourcedoesntexist
Source: "vendor\MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall skipifsourcedoesntexist

[Icons]
Name: "{group}\ImpedanceMCP"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\帮助文档（用户手册）"; Filename: "{app}\docs\用户手册.pdf"; Tasks: helpmenu
Name: "{group}\MCP 配置说明"; Filename: "{app}\docs\MCP兼容性说明.pdf"; Tasks: helpmenu
Name: "{group}\一键卸载 ImpedanceMCP（清除全部数据）"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ImpedanceMCP"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{autodesktop}\一键卸载 ImpedanceMCP"; Filename: "{uninstallexe}"; Tasks: uninstallicon

[Run]
; VC++ is only needed by the original classic exe; install silently if missing.
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "正在安装 Visual C++ 运行库…"; Flags: waituntilterminated skipifdoesntexist; Check: VCRedistMissing

; WebView2 is required by the native window (the app never opens a browser).
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; StatusMsg: "正在安装 Microsoft Edge WebView2 Runtime…"; Flags: waituntilterminated skipifdoesntexist; Check: WebView2Missing

; Write (or update) the ZCode MCP server entry, with a timestamped backup.
Filename: "{app}\{#MyAppMcpExeName}"; Parameters: "--configure-mcp zcode"; StatusMsg: "正在写入 ZCode MCP 配置…"; Flags: runhidden waituntilterminated runasoriginaluser; Tasks: mcpzcode

Filename: "{app}\{#MyAppExeName}"; Description: "启动 ImpedanceMCP"; Flags: nowait postinstall skipifsilent runasoriginaluser; Tasks: launch; Check: not WizardSilent

[UninstallRun]
; Stop running instances first; otherwise their EXE/WebView2 cache cannot be
; deleted and a "complete uninstall" would leave locked files behind.
Filename: "{sys}\taskkill.exe"; Parameters: "/F /T /IM ImpedanceMCP.exe"; Flags: runhidden waituntilterminated; RunOnceId: "ImpedanceMCPKillGui"
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM ImpedanceMCP_MCP.exe"; Flags: runhidden waituntilterminated; RunOnceId: "ImpedanceMCPKillMcp"
; Remove user data (API keys, uploads, reports), MCP entries and app registry keys
; before Inno removes the installation directory.  This is deliberately strict:
; the uninstaller is a "delete everything" uninstaller.
Filename: "{app}\{#MyAppMcpExeName}"; Parameters: "--cleanup --app-dir ""{app}"""; Flags: runhidden waituntilterminated; RunOnceId: "ImpedanceMCPDeepCleanup"

[UninstallDelete]
; Never keep user data or cached WebView2 state.  The cleanup above also
; enumerates all Windows profiles, which covers redirected AppData folders.
Type: filesandordirs; Name: "{localappdata}\ImpedanceMCP"
Type: filesandordirs; Name: "{userappdata}\ImpedanceMCP"
Type: filesandordirs; Name: "{app}\docs"
Type: filesandordirs; Name: "{app}\classic"

[Code]
function VCRedistMissing(): Boolean;
var
  Installed: Cardinal;
begin
  Result := True;
  if RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) then
    if Installed = 1 then Result := False;
  if RegQueryDWordValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) then
    if Installed = 1 then Result := False;
  if RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) then
    if Installed = 1 then Result := False;
end;

function WebView2Installed(): Boolean;
var
  Version: String;
begin
  Result := False;
  if RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True;
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True;
  if RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and (Version <> '') then
    Result := True;
  if DirExists(ExpandConstant('{commonpf32}\Microsoft\EdgeWebView\Application')) then
    Result := True;
  if DirExists(ExpandConstant('{localappdata}\Microsoft\EdgeWebView\Application')) then
    Result := True;
end;

function WebView2Missing(): Boolean;
begin
  Result := not WebView2Installed();
end;

function McrInstalled(): Boolean;
begin
  Result :=
    RegKeyExists(HKLM, 'SOFTWARE\MathWorks\MATLAB Runtime\R2023b') or
    RegKeyExists(HKLM, 'SOFTWARE\WOW6432Node\MathWorks\MATLAB Runtime\R2023b') or
    RegKeyExists(HKLM64, 'SOFTWARE\MathWorks\MATLAB Runtime\R2023b') or
    DirExists(ExpandConstant('{commonpf}\MATLAB\MATLAB Runtime\R2023b'));
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsWin64 then
  begin
    MsgBox('本程序需要 64 位 Windows 10/11（x64）。当前系统不是 64 位，无法安装。',
      mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WebView2Missing() then
    SuppressibleMsgBox('未能自动安装 Microsoft Edge WebView2 Runtime。' + #13#10 +
      '新版 ImpedanceMCP 使用原生窗口，需要 WebView2；请联网后重新运行安装程序，' + #13#10 +
      '或从 Microsoft 官网安装 Evergreen WebView2 Runtime。',
      mbInformation, MB_OK, IDOK);
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('classic') and (not McrInstalled()) then
    SuppressibleMsgBox('原版经典界面已安装，但未检测到 MATLAB Runtime R2023b。' + #13#10 +
      '新版 ImpedanceMCP 与 MCP 不需要 Runtime；' + #13#10 +
      '若要运行 classic\Impedance_Matching.exe，请安装 MyAppInstaller_mcr.exe（已内置 Runtime）或 MATLAB_Runtime_R2023b_Update_10_win64.zip。',
      mbInformation, MB_OK, IDOK);
end;
