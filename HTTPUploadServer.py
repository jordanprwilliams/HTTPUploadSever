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

# Also capture the chosen directory from the original parser
directory = args.directory

__version__ = "1.1"
__all__ = ["SimpleHTTPRequestHandler"]

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "SimpleHTTPWithUpload/" + __version__
    # Will be set by run()
    directory = os.getcwd()

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def do_GET(self):
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        ok, info = self.deal_post_data()
        print(ok, info, "by:", self.client_address)
        f = BytesIO()
        f.write(b'<!DOCTYPE html><html><title>Upload Result</title><body>')
        f.write(b"<h2>Upload Result</h2><hr>")
        f.write(b"<strong>Success: </strong>" if ok else b"<strong>Failed: </strong>")
        f.write(info.encode("utf-8"))
        ref = self.headers.get('referer', '/').encode()
        f.write(b'<br><a href="%s">back</a>' % ref)
        f.write(b"<hr><small>Created by Jordan Williams &copy; 2024</small></body></html>")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
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

        fn = os.path.basename(fileitem.filename)
        target_dir = self.translate_path(self.path)
        if not os.path.isdir(target_dir):
            target_dir = os.path.dirname(target_dir)

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
            for index in ("index.html", "index.htm"):
                index_path = os.path.join(path, index)
                if os.path.exists(index_path):
                    path = index_path
                    break
            else:
                return self.list_directory(path)

        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs.st_size))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Produce a directory listing (absent index.html)."""
        try:
            list_dir = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
        list_dir.sort(key=lambda a: a.lower())

        displaypath = html.escape(urllib.parse.unquote(self.path))
        parent_directory = '/' if self.path == '/' else '/'.join(self.path.rstrip('/').split('/')[:-1]) + '/'

        f = BytesIO()
        f.write(b'<!DOCTYPE html><html><head><title>HTTP Upload Server</title></head><body>')
        f.write(b"<h1>HTTP Upload Server</h1>")
        f.write(b"<p>Use this to upload, download, and navigate files.</p><hr>")
        f.write(b"<h2>Upload to %s</h2>" % displaypath.encode('utf-8'))
        f.write(b"<div style='margin:20px 0'>"
                b"<form ENCTYPE='multipart/form-data' method='post'>"
                b"<input name='file' type='file'> "
                b"<input type='submit' value='Upload'></form></div><hr>")
        f.write(b"<h2>Download From %s</h2>" % displaypath.encode('utf-8'))
        f.write(b"<p>Below is a list of files accessible for download:</p><ul>")
        if self.path != "/":
            f.write(b'<a href="%s" style="margin-bottom:20px; display:inline-block;">Back</a><br/>' % parent_directory.encode('utf-8'))
        for name in list_dir:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            elif os.path.islink(fullname):
                displayname = name + "@"
            f.write(b'<li><a href="%s">%s</a></li>' %
                    (urllib.parse.quote(linkname).encode('utf-8'),
                     html.escape(displayname).encode('utf-8')))
        f.write(b"</ul><hr><small>Created by Jordan Williams &copy; 2024</small></body></html>")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Map URL to filesystem under the handler's base directory."""
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        parts = [p for p in path.split('/') if p]

        base_dir = getattr(self, 'directory', os.getcwd())
        fs_path = base_dir
        for part in parts:
            if part in (os.curdir, os.pardir):
                continue
            fs_path = os.path.join(fs_path, part)
        return fs_path

    def guess_type(self, path):
        if not mimetypes.inited:
            mimetypes.init()
        base, ext = posixpath.splitext(path)
        return mimetypes.types_map.get(ext.lower(), 'application/octet-stream')

def run(server_class=http.server.ThreadingHTTPServer,
        handler_class=SimpleHTTPRequestHandler,
        port=8000, directory=None):
    handler_class.directory = directory or os.getcwd()
    httpd = server_class(('', port), handler_class)
    print(f"Starting http upload server on port {port} (dir: {handler_class.directory})...")
    httpd.serve_forever()

if __name__ == '__main__':
    # We already parsed args above; just use them here.
    run(port=port, directory=directory)
