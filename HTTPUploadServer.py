#!/usr/bin/env python3

"""
Simple HTTP Server With Upload.
This module builds on http.server by implementing the standard GET
and HEAD requests in a straightforward manner. Additionally, it supports
file uploads via POST requests.
"""

import os
import posixpath
import http.server
import urllib.parse
import cgi
import shutil
import mimetypes
import re
import html  # Import html for html.escape()
from io import BytesIO

__version__ = "0.1"
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
        """Process the uploaded file."""
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        content_length = int(self.headers['Content-Length'])
        pdict['CONTENT-LENGTH'] = content_length
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'}, keep_blank_values=1)
            fileitem = form['file']
            if fileitem.filename:
                fn = os.path.basename(fileitem.filename)
                open(fn, 'wb').write(fileitem.file.read())
                message = 'The file "' + fn + '" was uploaded successfully'
            else:
                message = 'No file was uploaded'
            return (True, message)
        return (False, "Something went wrong with the upload")

    def send_head(self):
        """Common code for GET and HEAD commands."""
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
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
        f.write(b"<html>\n<title>Directory listing for %s</title>\n" % displaypath.encode('utf-8'))
        f.write(b"<body>\n<h2>Directory listing for %s</h2>\n" % displaypath.encode('utf-8'))
        f.write(b"<hr>\n")
        f.write(b'<form ENCTYPE="multipart/form-data" method="post">')
        f.write(b'<input name="file" type="file"/>')
        f.write(b'<input type="submit" value="upload"/></form>\n')
        f.write(b"<hr>\n<ul>\n")
        
        # Add a Back link
        if parent_directory:
            f.write(b'<a href="%s">Back</a><br/>\n' % parent_directory.encode('utf-8'))

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
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax."""
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            path = os.path.join(path, word)
        return path

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

def run(server_class=http.server.HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd on port", port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()