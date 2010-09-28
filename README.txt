Copyright (c) 2008, German Aerospace Center (DLR)
All rights reserved.

= INTRODUCTION =
The data management system DataFinder primarily targets the management of 
scientific technical data. Data can be attached with individual meta data that 
is based on a free-definable data model to achieve data structuring 
and ordering. Moreover, the system is able to handle large amounts of data and 
can be easily integrated in existing working environments. The system is based 
upon a client-server-architecture and uses open, stable standards.

The server side consists of the meta data server that stores the meta data 
as well as the system configuration. The server is accessed with the standardized
protocol WebDAV – an extension of the HTTP protocol – by the client side. 
Data can be stored on the same server as the meta data or separated from it. 
The concept of separated meta data and data storage allows the flexible usage 
of heterogeneous storage resources. The access to these storage resources is 
achieved by using standardized data transfer interfaces. For example, FTP, File System, 
GridFTP, or WebDAV are currently supported.

= INFRASTRUCTURE INSTALLATION =
The DataFinder system consists of two clients one handling the data management related
and one handling the administrative tasks (e.g. data modeling, configuration of
storage resource, etc.). The minimum requirement concerning the server infrastructure is a 
WebDAV server which conforms to the WebDAV basic specification (RFC4918). The
WebDAV server stores configuration data, the logical data structure, and
optionally the managed data files. Examples of supported WebDAV servers are:
* Catacomb (open source)
* Apache + mod_dav (open source)
* Tamino 4.4 (commercial)

Currently, the best option is the Catacomb WebDAV server which implements additional
WebDAV specification (e.g. searching, access control) which in-turn 
are required for corresponding functionality of the DataFinder clients. For more
information on the Catacomb WebDAV server visit:
http://catacomb.tigris.org/

= CLIENT INSTALLATION =
== Source Distribution Installation ==
* Required Packages:
  * Python >= 2.6
  * PyQt 3.18.1 (Qt 3.3.8, SIP 4.10)
  * PyQt 4.7.3 (Qt 4.6.2, SIP 4.10)
  * Python WebDAV Library >= 0.1.2
  * Pyparsing >= 1.5.2
  * PyWin32 214 (Win32 only)
* Optional Packages:
  * Paramiko >= 1.7.4
  
* Install dependencies.
* Extract archive.
* Change to the created directory.
* (In some cases it is necessary to set the environment variable 'DF_HOME' to the path of the installation directory.)
* Start administrative client with 'python bin/datafinder-admin-client.py'.
* Start data management client with 'python bin/datafinder-client.py' (set environment variable 'DF_START' to a valid configuration URL).
 
== Binary Distribution Installation ==
* Extract archive.
* Change to the created directory.
* (In some cases it is necessary to set the environment variable 'DF_HOME' to the path of the installation directory.)
* Start administrative client with 'datafinder-admin-client[.exe]'.
* Start data management client with 'datafinder-client[.exe]' (set environment variable 'DF_START' to a valid configuration URL).
 
== Binary Windows Distribution Installation ==
* Start the corresponding installer.
* Start clients with the help of the created symbolic links.

= GETTING STARTED =
The DataFinder requires - as mentioned above - at least a WebDAV server conforming to the WebDAV base
specification RFC4918. After installation and starting of a corresponding 
WebDAV server please follow these steps:
* Start the administrative client.
* Cancel the login dialog and create a new configuration with 
  'File->Create Configuration...'.
* Chose 'File->Connect...' and connect to the created configuration (configuration URL and credentials are already inserted into the login dialog).
* The environment variable 'DF_START' has to be set to the configuration URL.
* Start the DataFinder data management client.

