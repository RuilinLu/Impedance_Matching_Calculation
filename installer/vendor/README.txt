Installer runtime bootstrappers
==============================

The compiled Setup.exe needs these two Microsoft bootstrappers at build time.
They are not committed to Git because they are large binaries. Download them
into this folder before running Inno Setup:

  MicrosoftEdgeWebview2Setup.exe
    https://go.microsoft.com/fwlink/p/?LinkId=2124703

  VC_redist.x64.exe
    https://aka.ms/vs/17/release/vc_redist.x64.exe

Then build the installer with Inno Setup 6:

  "C:\Users\<you>\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\ImpedanceMatchingAI.iss

Output: release\Impedance_Matching_AI_v4.4.0_Setup.exe
