V0.1 
# TODO
---
1. Upload a file via frontend.

2. backend scan file and update DB File table
---
# Features
1. Frontend file upload,download,bunck rename/delete/relocation
    a.  keep the original file metadata/attributes, like 'Date Created','Date Modified' etc.
    b.  dump each single file metadata/attributes to a local file like thumbnail files?

2.  Backend command line
    a. manually copy the file to the file location, then scan the folder, update database with files metadata.
    b. backup: pull database metadata out, copy the metadata with the files.

3.  useful features for endusers
    a. Find duplicated files, report, manybe delete and leave one copy only?
    b. Frontend resort/view  'Date Created', 'Title', 'Authors', 
    c. Backend manipulate files hirachy based on time
    YYYY 
       |_ MM
           |_ DD

v0.2
add file type support
    * images,
    * MD
    * csv
# database design

base 
node
item  *
file

polymorphism

https://realpython.com/modeling-polymorphism-django-python/