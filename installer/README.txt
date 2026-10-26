智配芯生 · ImpedanceMCP v4.3.0
================================

安装完成后：

1. 双击桌面/开始菜单的 “ImpedanceMCP” 打开原生窗口（不会出现命令行或浏览器）；
2. 首次使用 AI 对话时，在「设置」中选择服务商、模型，并填写你自己的 API Key；
3. 不配置 AI 也可以使用全部匹配设计、圆图、扫描、耐压和报告功能；
4. MCP：运行 ImpedanceMCP_MCP.exe --mcp 即可作为 stdio MCP 服务器；
   HTTP/SSE：ImpedanceMCP_MCP.exe --mcp --http 8790。

一键卸载（清除全部数据）：
  开始菜单 → “一键卸载 ImpedanceMCP（清除全部数据）”
  或 {安装目录}\unins000.exe
  会关闭运行中的程序，并删除程序、用户数据、API Key、上传/报告、
  WebView2 缓存、MCP 配置、快捷方式和注册表项，不保留任何残留。

帮助文档：
  {安装目录}\docs\用户手册.pdf
  {安装目录}\docs\MCP兼容性说明.pdf
  {安装目录}\docs\计算正确性审计.pdf
  {安装目录}\docs\安装与杀毒软件说明.pdf

原版经典界面：
  {安装目录}\classic\Impedance_Matching.exe
  需要 MATLAB Runtime R2023b；新版软件与 MCP 不需要 Runtime。
  若缺少 Runtime，可安装项目提供的 MyAppInstaller_mcr.exe（已内置 Runtime）。

用户数据：
  %LOCALAPPDATA%\ImpedanceMCP\
  一键卸载会删除上述目录（包括 data、webview 缓存）。

开发者：卢瑞林、卢柯吉、林芷伊、张昀蕾
联系：radarlurui@gmail.com ｜ Lu_Skywalker2915@sjtu.edu.cn
GitHub：https://github.com/RuilinLu/Impedance_Matching_Calculation
