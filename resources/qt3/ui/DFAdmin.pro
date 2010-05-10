TEMPLATE	= app
LANGUAGE	= C++

CONFIG	+= qt warn_on release

FORMS	= AdminMainWindowForm.ui \
	SelectScriptDialog.ui \
	FullLoginDialog.ui \
	SelectIconDialog.ui \
	DataStoreConfigurationWizard.ui \
	EditAddDataTypeDialog.ui \
	EditAddRelationTypeDialog.ui \
	create_configuration_dialog.ui \
	license_dialog.ui

IMAGES	= ../images/nolock.png \
	../images/properties24.png \
	../images/refresh24.png \
	../images/search24.png \
	../images/newAny16.png \
	../images/openAny16.png \
	../images/saveAny16.png \
	../images/openAny24.png \
	../images/saveAny24.png \
	../images/deleteAny16.png \
	../images/deleteAny24.png \
	../images/newAny24.png \
	../images/saveAsAny16.png \
	../images/saveAsAny24.png \
	../images/personAny16.png \
	../images/personAny24.png \
	../images/userAdd16.png \
	../images/userAdd24.png \
	../images/close_file24.png \
	../images/delete24.png \
	../images/edit24.png \
	../images/help24.png \
	../images/new24.png \
	../images/open24.png \
	../images/preferences24.png \
	../images/prop24.png \
	../images/reset24.png \
	../images/save24.png \
	../images/save_as24.png \
	../images/export24.png \
	../images/import24.png \
	../images/exit24.png \
	../images/folder_open16.png \
	../images/folder_closed16.png \
	../images/new16.png \
	../images/dir_close.png \
	../images/dir_open.png \
	../images/simley_face16.png \
	../images/users16.png \
	../images/user_add24.png \
	../images/clown1.png \
	../images/DF_Logo_klein_trans.png \
	../images/about24.png \
	../images/connect24.png \
	../images/disconnect24.png \
	../images/relationType24.png \
	../images/dataStore24.png \
	../images/dataType24.png \
	../images/newDataStore24.png \
	../images/newDataType24.png \
	../images/newRelationType24.png \
	../images/refresh24.png \
	../images/save_all24.png \
	../images/newUser24.png \
	../images/newGroup24.png

unix {
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}
