# Flask File Hoster
Easy file hoster with Flask

# How does it work ?
- Make a `files` folder
- Inside it, you can put any file you want
- Files will not be public/private if you didn't add them in files.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<files>
    <file>
        <mimetype>text/plain</mimetype> <!-- Mimetype to tell the browser how to display -->
        <name>demo_private</name> <!-- The filename in files folder -->
        <isPublic>false</isPublic> <!-- Is visible in / -->
        <password>helloworld</password> <!-- The secret password -->
    </file>
</files>
```

File structure
```
files
|----cv.pdf
|----minecraft_mod.jar
main.py
requirements.txt
files.xml
```
