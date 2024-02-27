# HTTPUploadServer
**A Simple and User-Friendly File Management Tool**
This Python-based web server allows you to easily upload, download, and manage files through a web browser or command-line tools. It is designed to be spun up and taken down quickly to transfer files. Important: File transfers are not secure and could be intercepted. Consider this server for development or controlled environments only.

**Features:**
* **File Uploads:** Upload files directly from your browser or using tools like `curl`.
* **Directory Browsing:** Navigate through your file system and download files with ease.
* **Command-Line Friendly:** Supports file management using `curl` and `wget`.

**Caution:**
Running the server exposes files and directories to the chosen port.

Exercise extreme caution before running this script on a public network or any untrusted environment. Here's why:

Unencrypted Connections: By default, this script uses HTTP, which transmits data unsecured. This means anyone on the network can intercept and potentially modify the data being transmitted, including uploaded files and directory listings.
Full Directory Exposure: Running the server in the current directory exposes all files and subdirectories accessible through the chosen port. Attackers could use this information to identify vulnerabilities or exploit sensitive data.
Recommendations:

Use HTTPS: If running the server is necessary, strongly consider using HTTPS (TLS/SSL) to encrypt communication and protect data confidentiality and integrity. This requires obtaining a valid SSL certificate and configuring the server appropriately.
Limit Directory Access: Avoid running the server in directories containing sensitive information. Create a dedicated directory with only the necessary files for upload/download purposes.
Restrict Access: If possible, implement access controls (e.g., user authentication and authorization) to restrict access to the server to authorized users.
Public Networks: Never run this script on a public network without robust security measures in place. The risks of data exposure and unauthorized access are significantly increased.
Additional Considerations for Encrypted Connections:

Using HTTPS requires setting up a secure server environment with a valid SSL/TLS certificate. This can involve additional configuration and technical expertise.
Even with HTTPS, consider the points mentioned above regarding directory access and potential vulnerabilities within the script itself.
Remember: Security is critical, especially when handling sensitive information. Use this script with caution and prioritize secure connections and controlled access to protect your data.

**Prerequisites:**
* Python 3 installed on your system.

**Installation:**
1. Clone the repository:
Use code with caution.
```git clone https://github.com/jordanprwilliams/HTTPUploadServer.git```

2. Navigate to the project directory:
```cd HTTPUploadServer```

**Running the Server:**
### Usage
```python3 HTTPUploadServer.py [OPTIONS]```

**Options:**
* `-p PORT`: Specify the port number on which the server listens. (Default: 8000)
* `-d DIRECTORY`: Specify the directory containing the files to be served. (Default: current working directory)

**Example:**
```python3 HTTPUploadServer.py -p 8080 -d /var/www/html```

This command will start the server on port 8080, serving files from the `/var/www/html` directory.

Then Browse for the file you want select it and click upload

### Downloading Files
**Using wget:**
wget http://localhost:<PORT>/file.txt

**Using curl:**
curl -o file.txt http://localhost:<PORT>/file.txt

**Note:** Replace `<PORT>` with the actual port number you specified when running the server.

### Uploading Files
To upload a file, use a web browser and navigate to the following URL:
```http://localhost:<PORT>/```

Drag and drop the desired file(s) into the browser window to upload them to the specified directory.

Alternatively you can upload files using curl```curl -T file.txt http://localhost:<PORT>/```

**License:**
This software is distributed under the terms of the GNU General Public License v3 (GPLv3), available in the `LICENSE.md` file and at [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

**Additional Notes:**

* Consider adding a license section specifying how users can distribute and modify the code.
* You can include a screenshot demonstrating the server's interface to enhance the README.