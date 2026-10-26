ImpedanceMCP installer vendor files
====================================

The following binaries are intentionally not committed to Git (large / third-party).
Place them in this directory before running ISCC:

1. VC_redist.x64.exe
   https://aka.ms/vs/17/release/vc_redist.x64.exe

2. MicrosoftEdgeWebview2Setup.exe
   https://go.microsoft.com/fwlink/p/?LinkId=2124703
   (Microsoft Edge WebView2 Evergreen Bootstrapper)

3. classic\Impedance_Matching.exe
   Copy the original V3.0 MATLAB Compiler output from:
   APP_Release_Release_Version/for_redistribution_files_only/Impedance_Matching.exe

Then build:
   iscc /Qp installer\ImpedanceMCP.iss
