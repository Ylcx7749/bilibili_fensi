Outfile "BilibiliFansMonitor_Setup.exe"
InstallDir "$PROGRAMFILES\BilibiliFansMonitor"
RequestExecutionLevel admin
SetCompressor lzma

Page directory
Page instfiles

Section "Install"
  SetOutPath $INSTDIR
  File /r "dist\BilibiliFansMonitor\*.*"

  CreateShortcut "$DESKTOP\Bilibili粉丝观测站.lnk" "$INSTDIR\BilibiliFansMonitor.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\BilibiliFansMonitor.exe"
  Delete "$DESKTOP\Bilibili粉丝观测站.lnk"
  RMDir /r "$INSTDIR"
SectionEnd