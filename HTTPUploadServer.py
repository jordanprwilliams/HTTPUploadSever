#!/usr/bin/env python3
"""
Simple HTTP Server with Upload
This Python-based web server allows you to easily upload, download, and manage files through a web browser or command-line tools. It is designed to be spun up and taken down quickly for file transfer.

**Important:** 
File transfers are **not secure** and could be intercepted. Consider using this server only for development or controlled environments.

**Features:**
* Serve files and directories over HTTP.
* Enable file uploads to a specified directory (`-d` option) using a simple web form.
* Allow navigation through directories and downloading of files via a web browser.
* Provide basic directory listings.

**Usage:**
```python3 HTTPUploadServer.py [options]```

Options:
* `-p PORT`: Specify the port number for the server to listen on. (Default: 8000)
* `-d DIRECTORY`:  Specify the directory to serve files from and upload to. (Default: current working directory)
* `-h`, `--help`: Display help information and usage instructions.
"""
import os
import posixpath
import http.server
import urllib.parse
import cgi
import shutil
import mimetypes
import re
import sys
import html  # Import html for html.escape()
import argparse
from io import BytesIO
from http.server import HTTPServer

# Initialize the argument parser
parser = argparse.ArgumentParser(description='Simple HTTP Server With Upload.')
parser.add_argument('-p', '--port', type=int, default=8000, help='Specifies the port number the server listens on. Default is 8000.')
parser.add_argument('-d', '--directory', help='Specify the directory to serve files from', default=os.getcwd())
args = parser.parse_args()
# Use the port argument value
port = args.port

__version__ = "1.0"
__all__ = ["SimpleHTTPRequestHandler"]

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "SimpleHTTPWithUpload/" + __version__
    
    def copyfile(self, source, outputfile):
        """
        Copy all data between two file objects.
        The SOURCE argument is a file object open for reading (or anything with a read() method)
        and the OUTPUTFILE argument is a file object open for writing (or anything with a write() method).
        """
        shutil.copyfileobj(source, outputfile)

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<html>\n<title>Upload Result Page</title>\n")
        f.write(b"<body>\n<h2>Upload Result Page</h2>\n")
        f.write(b"<hr>\n")
        if r:
            f.write(b"<strong>Success:</strong>")
        else:
            f.write(b"<strong>Failed:</strong>")
        f.write(bytes(info, "utf-8"))
        f.write(b"<br><a href=\"%s\">back</a>" % self.headers['referer'].encode())
        f.write(b"<hr><small>Powered By: Your Name Here</small></hr>")
        f.write(b"</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()

    def deal_post_data(self):
    """Process file upload to the served directory."""
    ctype, pdict = cgi.parse_header(self.headers.get('content-type', ''))
    if ctype != 'multipart/form-data':
        return (False, "Invalid content-type (expected multipart/form-data)")

    boundary = pdict.get('boundary')
    if isinstance(boundary, str):
        pdict['boundary'] = boundary.encode()
    pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-Length', '0'))

    form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                            environ={'REQUEST_METHOD': 'POST'},
                            keep_blank_values=True)

    if 'file' not in form:
        return (False, "No file field in form")

    fileitem = form['file']
    if not getattr(fileitem, 'filename', ''):
        return (False, "No file selected")

    # Normalise filename and target directory
    fn = os.path.basename(fileitem.filename)
    target_dir = self.translate_path(self.path)
    if not os.path.isdir(target_dir):
        target_dir = os.path.dirname(target_dir)  # if posting while viewing a file

    target_path = os.path.join(target_dir, fn)

    try:
        with open(target_path, 'wb') as out:
            shutil.copyfileobj(fileitem.file, out)
        return (True, f'The file "{fn}" was uploaded successfully')
    except Exception as e:
        return (False, f'Failed to save file: {e}')

def send_head(self):
    """Serve a file or a directory listing."""
    path = self.translate_path(self.path)
    if os.path.isdir(path):
        # If index.* exists, serve it; otherwise list directory
        for index in ("index.html", "index.htm"):
            index_path = os.path.join(path, index)
            if os.path.exists(index_path):
                path = index_path
                break
        else:
            return self.list_directory(path)

    # If we’re here, path should be a file
    ctype = self.guess_type(path)
    try:
        f = open(path, 'rb')
    except OSError:
        self.send_error(404, "File not found")
        return None

    self.send_response(200)
    self.send_header("Content-type", ctype)
    fs = os.fstat(f.fileno())
    self.send_header("Content-Length", str(fs.st_size))
    self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
    self.end_headers()
    return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html)."""
        try:
            list_dir = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list_dir.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = html.escape(urllib.parse.unquote(self.path))
  
        # Calculate parent directory (going back one level)
        parent_directory = '/' if self.path == '/' else '/'.join(self.path.rstrip('/').split('/')[:-1]) + '/'

        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<html>\n<head><title>HTTP Upload Server</title></head>\n")
        f.write(b"<body>\n<h1>HTTP Upload Server</h1>\n")
        f.write(b"<p>Welcome to the HTTP Upload Server. Use this interface to upload, download, and navigate files.</p>\n")
        f.write(b"<hr>\n")
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<body>\n<h2>Upload to %s</h2>\n" % displaypath.encode('utf-8'))
        f.write(b"<hr>\n")
        # Instructions for uploading files with improved formatting
        f.write(b"<div style='margin-top: 20px; margin-bottom: 20px;'>\n")
        f.write(b"<p>To upload a file, choose a file using the 'Browse' button, then click 'Upload' to transfer your file to the server:</p>\n")
        f.write(b'<form ENCTYPE="multipart/form-data" method="post" style="margin-bottom: 20px;">\n')
        f.write(b'<input name="file" type="file" style="margin-bottom: 10px;"/> ')
        f.write(b'<input type="submit" value="Upload" style="margin-left: 10px;"/></form>\n')
        f.write(b"</div><hr>\n")
        # Line indicating files accessible for download
        f.write(b"<body>\n<h2>Download From %s</h2>\n" % displaypath.encode('utf-8'))
        f.write(b"<p>Below is a list of files accessible for download:</p>\n<ul>\n")
        # Condition to show "Back" link only if not in the root directory
        if self.path != "/":
            f.write(b'<a href="%s" style="margin-bottom:20px; display:inline-block;">Back</a><br/>\n' % parent_directory.encode('utf-8'))
        #Lists file in Directory
        for name in list_dir:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            elif os.path.islink(fullname):
                displayname = name + "@"
            # Write the directory item
            f.write(b'<li><a href="%s">%s</a></li>\n' % (urllib.parse.quote(linkname).encode('utf-8'), html.escape(displayname).encode('utf-8')))

        f.write(b"</ul>\n<hr>\n</body>\n</html>\n")
        f.write(b"<small>Created by Jordan Williams &copy; 2024</small>\n")  # Custom text addition
        f.write(b"</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f
        
def translate_path(self, path):
    """Map URL to filesystem under the handler's base directory."""
    # strip query/fragment
    path = path.split('?', 1)[0].split('#', 1)[0]
    path = urllib.parse.unquote(path)
    path = posixpath.normpath(path)
    parts = [p for p in path.split('/') if p]

    base_dir = getattr(self, 'directory', os.getcwd())
    fs_path = base_dir
    for part in parts:
        # prevent path traversal
        if part in (os.curdir, os.pardir):
            continue
        fs_path = os.path.join(fs_path, part)
    return fs_path

    def guess_type(self, path):
        """Guess the type of a file based on its filename."""
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # Initialize MIME types if not already done
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        # Add more mappings if necessary
    })

# Modify the run function to accept a port argument
def run(server_class=http.server.HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000, directory=None):
    server_address = ('', port)
    # Assign root directory from the args
    handler_class.directory = directory or os.getcwd()
    httpd = server_class(server_address, handler_class)
    print(f"Starting http upload server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
	    port = 8080  # Default port
"""
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])  # Convert the first command-line argument to an integer for the port
    except ValueError:
        print("Warning: Port argument must be an integer. Using default port 8000.")
    
    run(port=port)
"""
if __name__ == '__main__':
  # Argument parsing
  parser = argparse.ArgumentParser(description='Simple HTTP Server With Upload.')
  parser.add_argument('-p', '--port', type=int, default=8000, help='Specifies the port number the server listens on. Default is 8000.')
  parser.add_argument('-d', '--directory', type=str, default=os.getcwd(),
                      help='Directory to serve files from and upload to. Defaults to the current working directory.')
  args = parser.parse_args()

  # Use the specified port or the default
  port = args.port

  # Use the specified directory or the default
  directory = args.directory

  run(port=args.port, directory=args.directory)

