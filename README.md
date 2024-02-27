# HTTPUploadServer
**A Simple and User-Friendly File Management Tool**

This Python-based web server allows you to easily upload, download, and manage files through a web browser or command-line tools.

**Features:**
* **Secure File Uploads:** Upload files directly from your browser or using tools like `curl`.
* **Directory Browsing:** Navigate through your file system and download files with ease.
* **Command-Line Friendly:** Supports file management using `curl` and `wget`.

**Prerequisites:**
* Python 3 installed on your system.

**Installation:**
1. Clone the repository:
Use code with caution.
```git clone https://github.com/jordanprwilliams/HTTPUploadServer.git```

2. Navigate to the project directory:

```cd HTTPUploadServer```

**Running the Server:**
1. Start the server on the default port (8080):
```python3 HTTPUploadServer.py```


2. To specify a different port, use the `-p` option:
```python3 HTTPUploadServer.py -p 80```


**Caution:**
Running the server makes all files in the current directory and subdirectories accessible through the web server. Use caution when running on public networks.

**License:**
This software is distributed under the terms of the GNU General Public License v3 (GPLv3), available in the `LICENSE.md` file and at [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

**Additional Notes:**

* Consider adding a license section specifying how users can distribute and modify the code.
* You can include a screenshot demonstrating the server's interface to enhance the README.