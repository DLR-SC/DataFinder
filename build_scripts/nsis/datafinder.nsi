!include "MUI.nsh" ; MUI 1.67 compatible
!include "winmessages.nsh"
!include definitions.nsi 

!define HKLM_ENVIRONMENT_VARIABLE 'HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"' ; HKLM (all users)


!ifdef WITH_USER_CLIENT
    !define PRODUCT_NAME_USER_CLIENT "${PRODUCT_NAME}"
    !define PRODUCT_FULL_NAME_USER_CLIENT "${PRODUCT_NAME_USER_CLIENT}_${PRODUCT_VERSION}"
!endif

!ifdef WITH_ADMIN_CLIENT
    !define PRODUCT_NAME_ADMIN_CLIENT "${PRODUCT_NAME} Administration"
    !define PRODUCT_FULL_NAME_ADMIN_CLIENT "${PRODUCT_NAME_ADMIN_CLIENT}_${PRODUCT_VERSION}"
!endif

!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}_${PRODUCT_VERSION}"

!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir_${PRODUCT_NAME}_${PRODUCT_VERSION}"

SetCompressor lzma

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install-blue.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall-blue.ico"

!define MUI_HEADERIMAGE

; Welcome page
!define MUI_WELCOMEPAGE_TITLE_3LINES
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${PRODUCT_NAME}-${PRODUCT_VERSION}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_TITLE_3LINES
!ifdef WITH_USER_CLIENT
    !define MUI_FINISHPAGE_RUN "$INSTDIR\${USER_CLIENT_EXECUTABLE_NAME}"
!else
    !ifdef WITH_ADMIN_CLIENT
        !define MUI_FINISHPAGE_RUN "$INSTDIR\${ADMIN_CLIENT_EXECUTABLE_NAME}"
    !endif
!endif

!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "German"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_OUTFILE}"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}-${PRODUCT_VERSION}"
ShowInstDetails show
ShowUnInstDetails show

Section "Hauptgruppe" SEC01
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  SetOverwrite on
  
  !ifndef WITH_USER_CLIENT
    File /r /x ${USER_CLIENT_EXECUTABLE_NAME} "${DISTRIBUTION_DIR}\*.*"
  !else 
    !ifndef WITH_ADMIN_CLIENT
      File /r /x ${ADMIN_CLIENT_EXECUTABLE_NAME} "${DISTRIBUTION_DIR}\*.*"
    !else
      File /r "${DISTRIBUTION_DIR}\*.*"
    !endif
  !endif
  
  ; Write Environment variable
  System::Call 'Kernel32::SetEnvironmentVariableA(t, t) i("DF_START", "${START_URL}").r0'
  WriteRegExpandStr ${HKLM_ENVIRONMENT_VARIABLE} "DF_START" ${START_URL}
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
 
  
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  !ifdef WITH_USER_CLIENT
      CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_FULL_NAME_USER_CLIENT}.lnk" "$INSTDIR\${USER_CLIENT_EXECUTABLE_NAME}" "" "$INSTDIR\${USER_CLIENT_ICON}" "0"
      CreateShortCut "$DESKTOP\${PRODUCT_FULL_NAME_USER_CLIENT}.lnk" "$INSTDIR\${USER_CLIENT_EXECUTABLE_NAME}" "" "$INSTDIR\${USER_CLIENT_ICON}" "0"
  !endif
  !ifdef WITH_ADMIN_CLIENT
      CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_FULL_NAME_ADMIN_CLIENT}.lnk" "$INSTDIR\${ADMIN_CLIENT_EXECUTABLE_NAME}" "" "$INSTDIR\${ADMIN_CLIENT_ICON}" "0"
      CreateShortCut "$DESKTOP\${PRODUCT_FULL_NAME_ADMIN_CLIENT}.lnk" "$INSTDIR\${ADMIN_CLIENT_EXECUTABLE_NAME}" "" "$INSTDIR\${ADMIN_CLIENT_ICON}" "0"
  !endif
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Zur Support Webseite.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Programm entfernen.lnk" "$INSTDIR\Uninstall.exe"
  
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\DataFinder_User.ico"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "${PRODUCT_STARTMENU_REGVAL}" "$ICONS_GROUP"
  !ifdef WITH_USER_CLIENT
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "PRODUCT_FULL_NAME_USER_CLIENT" "${PRODUCT_FULL_NAME_USER_CLIENT}"
  !endif
  !ifdef WITH_ADMIN_CLIENT
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "PRODUCT_FULL_NAME_ADMIN_CLIENT" "${PRODUCT_FULL_NAME_ADMIN_CLIENT}"
  !endif
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"

  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "ProductID"      "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "RegOwner"       "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "RegCompany"     "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "HelpLink"       "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "HelpTelephone"  "+49 (0) 531 295 3341"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout"   "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLUpdateInfo"  "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoModify"     "1"
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoRepair"     "1"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) wurde erfolgreich deinstalliert."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Möchten Sie $(^Name) und alle seinen Komponenten deinstallieren?" IDYES +2
  Abort
FunctionEnd

Var PFN
Var PTN
Section Uninstall
  SetShellVarContext all
  ReadRegStr $ICONS_GROUP ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "${PRODUCT_STARTMENU_REGVAL}"
  !ifdef WITH_USER_CLIENT
    ReadRegStr $PFN ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "PRODUCT_FULL_NAME_USER_CLIENT"
    Delete "$DESKTOP\$PFN.lnk"
    Delete "$SMPROGRAMS\$ICONS_GROUP\$PFN.lnk"
  !endif
  !ifdef WITH_ADMIN_CLIENT
    ReadRegStr $PTN ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "PRODUCT_FULL_NAME_ADMIN_CLIENT"
    Delete "$DESKTOP\$PTN.lnk"
    Delete "$SMPROGRAMS\$ICONS_GROUP\$PTN.lnk"
  !endif
  
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\Uninstall.exe"

  Delete "$SMPROGRAMS\$ICONS_GROUP\Programm entfernen.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Zur Support Webseite.lnk"
  
  RMDir /r "$SMPROGRAMS\$ICONS_GROUP"
  RMDir /r "$INSTDIR"
  
  DeleteRegValue ${HKLM_ENVIRONMENT_VARIABLE} DF_START
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd
