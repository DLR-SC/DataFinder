To package a script extension in the required tar archive format you can use the build command "package_script_extension".
This build command assumes a script extension file directory layout as follows:

script_extensions
      |--- My Script Extension 1
      |             |--- lib
      |             |     |--- common_lib.py 
      |             |--- src
      |                   |--- my_package
      |                           |--- common.py
      |                           |--- report1.py
      |                           |--- report2.py
      |                           |--- SCRITPS
      |                           |--- PreferencesPage.py
      |--- My Script Extension 2
                    |--- ...
                         
Python source code below the "lib" folder is included as well and is accessible by the script extension.

Python source code of the script extension itself is put below the "src" folder.

The file "SCRIPTS" contains a list of all provided scripts of this script extension and could look as follows:
report1.py
report2.py

The file "PreferencesPage.py" can contain a custom preference page.
