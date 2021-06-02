This folder should contain .lib files for opencv and some others.
XXX is the opencv version number. 

opencv_worldXXX.lib
opencv_worldXXXd.lib
spdlog.lib

Note that these lib files will not be uploaded to the git server. 

QT lib files require you to set an environment variable, "QT_DIR" 
that points to "QT_INSTALLDIR\QT_VERSION\QT_COMPILER\".
For example: "C:\dev\qt\5.15.2\msvc2019_64", a folder which contains
".\lib" and all the .lib files needed for linking.