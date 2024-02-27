# HTTPUploadServer



A simple, lightweight HTTP server for file uploads and directory listing, designed for quick file management and sharing over networks. Built with Python, it allows users to easily upload, download, and navigate through files in any browser or via command line using tools like `curl` and `wget`.



## Features



- **File Upload**: Securely upload files through your browser or via `curl`.

- **Directory Browsing**: Navigate through directories and download files with ease.

- **Command Line Friendly**: Supports file downloading and uploading using command line tools.



## Getting Started



### Prerequisites



Ensure you have Python installed on your system. This server was developed with Python 3 in mind.



### Installation



Clone the repository to your local machine:

git clone https://github.com/jordanprwilliams/HTTPUploadSever.git


Navigate into the project directory:


### Running the Server

Start the server w
python3 HTTPUploadServer

This will start on default port of 8080

to specify your own port you can use the -p option

python3 HTTPUploadServer.py -p 80

### Warning

The web server will mabe all files in the directory your running from and sub directories accessible from the now open port via the web server
