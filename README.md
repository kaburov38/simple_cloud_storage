# simple_cloud_storage
## Description
This simple cloud storage use nameko, mysql and redis. This project has 2 services. The account service will handle the register and login. While the storage service will handle the upload and download of files. The uploaded file will be stored in the storage folder with a hashed name while the real file name will be stored in the database. Users have to be log in first before uploading or downloading file. Users can only download their own file.