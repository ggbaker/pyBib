Note: I've pretty much abandoned this project. At some point I may go back and try to reimplement and improve this with a native iPadOS app...

I ended up implementing the import features I needed using the native Shortcuts app (see here: https://github.com/ggbaker/iOS-BibTeX-Shortcuts).

For reading .bib files, I've been using the References app by Benjamin Burton (see here: https://sites.google.com/site/appsformaths/references). 

# pyBib
pyBib is a very basic bibTeX reader (and eventually editor) for the iPad (using the Pythonista app)

To use this app, you must have the Pythonista app installed on your iPad. I recommend using StaSh (https://github.com/ywangd/stash) to pip install required packages (and use git).

Use the pyBib Settings app to configure your Dropbox access token (see https://www.dropbox.com/developers for help), and to specify the path
in Dropbox to the bib file.

A homepage icon can be created using the 'Shortcuts' app (formerly Workflow).

This app is designed around my bibTeX/Jabref workflow which uses the 'Keywords' field to specify groupings of entries. Eventually, the program will allow editing and adding new entries.
