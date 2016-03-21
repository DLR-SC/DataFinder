Copyright (c) 2008, German Aerospace Center (DLR)
All rights reserved.

# Introduction
The data management system DataFinder primarily targets the management of 
scientific technical data. Data can be attached with individual meta data that 
is based on a free-definable data model to achieve data structuring 
and ordering. Moreover, the system is able to handle large amounts of data and 
can be easily integrated in existing working environments. The system is based 
upon a client-server-architecture and uses open, stable standards.

The server side consists of the meta data server that stores the meta data 
as well as the system configuration. The server is accessed with the standardized
protocol WebDAV - an extension of the HTTP protocol - by the client side.
Data can be stored on the same server as the meta data or separated from it. 
The concept of separated meta data and data storage allows the flexible usage 
of heterogeneous storage resources. The access to these storage resources is 
achieved by using standardized data transfer interfaces. For example, FTP, File System, 
GridFTP, or WebDAV are currently supported.

# Infrastructure Installation
The DataFinder system consists of two clients one handling the data management related
and one handling the administrative tasks (e.g. data modeling, configuration of
storage resource, etc.). The minimum requirement concerning the server infrastructure is a 
WebDAV server which conforms to the WebDAV basic specification (RFC4918). The
WebDAV server stores configuration data, the logical data structure, and
optionally the managed data files. Examples of supported WebDAV servers are:
* Catacomb (open source)
* Apache + mod_dav (open source)
* Subversion

Currently, the best option is the Catacomb WebDAV server which implements additional
WebDAV specification (e.g. searching, access control) which in-turn 
are required for corresponding functionality of the DataFinder clients. For more
information on the Catacomb WebDAV server visit:
http://catacomb.tigris.org/

# Client Installation
## Source Distribution Installation
* Required Packages:
  * Python >= 2.6
  * Pyparsing >= 1.5.2
* GUI clients only
   * PyQt 3.18.1 (Qt 3.3.8, SIP 4.10)
   * PyQt 4.7.3 (Qt 4.6.2, SIP 4.10)
* Win32 only
   * PyWin32 214 (Win32 only) 
* Optional Packages (at least the WebDAV library or the Subversion package is required):
  * Python WebDAV Library >= 0.3.0
  * paramiko >= 1.7.4
  * nose 0.11.1
  * pysvn >=1.7.2
  * boto >= 2.0rc1
* Install dependencies.
  * Extract archive.
  * Change to the created directory.
  * Run to verify your environment: $> python setup.py test
    (Set --nosecommand to the complete path of the nose Python start script if not found; e.g., --nosecommand=/usr/local/bin/nosetests)
  * Run to install: $> python setup.py install 

Script API distribution:
* Try the script examples in contrib/script_examples.

GUI client distribution:
* Start administrative client with 'python datafinder-admin-client.py'.
* Start data management client with 'python datafinder-client.py'.
 
## Binary Distribution Installation
* Extract archive.
* Change to the created directory.
* Start administrative client with 'datafinder-admin-client[.exe]'.
* Start data management client with 'datafinder-client[.exe]'.
 
## Binary Windows Distribution Installation
* Start the corresponding installer.
* Start clients with the help of the created symbolic links.

# Getting started
The DataFinder requires - as mentioned above - at least a WebDAV server conforming to the WebDAV base
specification RFC4918. After installation and starting of a corresponding 
WebDAV server please follow these steps:
* Start the administrative client.
* Cancel the login dialog and create a new configuration with 
  'File->Create Configuration...'.
* Chose 'File->Connect...' and connect to the created configuration (configuration URL and credentials are already inserted into the login dialog).
* The environment variable 'DF_START' can be set to the configuration URL.
* Start the DataFinder data management client.

More detailed information is available on: https://wiki.sistec.dlr.de/DataFinderOpenSource
