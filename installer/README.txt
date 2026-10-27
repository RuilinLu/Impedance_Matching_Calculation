Impedance Matching AI v4.5.0

安装内容：
  ImpedanceMatchingAI.exe       主程序（原生 WebView2 窗口）
  ImpedanceMatchingAI_MCP.exe   MCP stdio / HTTP 服务
  docs\                         离线说明书（HTML + 界面截图 + MathJax）
  TextBook\                     用户教材入口（可选）
  README.md / CHANGELOG.md / SECURITY.md / THIRD_PARTY_NOTICES.md

用户数据：
  %LOCALAPPDATA%\ImpedanceMatchingAI\
    data\config.json             模型服务与 API Key（仅本机）
    data\library\index.sqlite3   教材全文索引 / OCR / 翻译缓存
    data\uploads\                聊天附件
    data\reports\                导出的报告
    TextBook\                    用户教材

安装程序会：
  1. 检测并安装 Microsoft VC++ 运行库（如缺失）；
  2. 检测并安装 Microsoft Edge WebView2 Runtime（如缺失）；
  3. 创建教材数据库与 TextBook 目录；
  4. 创建开始菜单、可选桌面快捷方式与“一键卸载”。

卸载：
  使用开始菜单/桌面的“一键卸载 Impedance Matching AI”。卸载器会用复选框询问是否
  保留 API Key、模型连接、界面设置、上传、报告、教材索引与缓存：
  - 默认勾选“保留”：下次安装会自动检测并复用这些数据；
  - 取消勾选：彻底删除 %LOCALAPPDATA%\ImpedanceMatchingAI 下的个人数据（不可恢复）。
  共享的 WebView2 Runtime 不会被删除。

系统要求：Windows 10/11 x64。
