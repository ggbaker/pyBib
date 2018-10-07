import ui
import dropbox
import bibtexparser
import re
from shutil import copyfile
# import dropbox key (dbx) and filepath to bib file from settings file
import dropbox
from pyBibSettings import dbx, libFilepath


def initial_load():
	""" Run on launch """
	global \
		connectionStatus, \
		allBibData, \
		allDisplayEntries, \
		textBibData, \
		currentlyShowing, \
		keywordsList
	
	# Attempt to download bib file
	download_and_store()
	
	# Load ui pane and populate tables
	load_ui()
	fill_keywords_menu(keywordsList)
	fill_entries_menu(currentlyShowing.displayEntries)


def download_and_store():
	""" download_and_store attempts to download the bib file from the Dropbox path
	specified in the pyBibSettings.py file. If it succeeds, it sets the connection
	flag to 1. If it fails, the flag is set to zero, and the last saved bib file
	is used. It then parses the bib file """
	global \
		connectionStatus, \
		allBibData, \
		allDisplayEntries, \
		textBibData, \
		currentlyShowing, \
		keywordsList
		
	try:
		# Try to get file from Dropbox
		metadata, file = dbx.files_download(path=libFilepath)
		connectionStatus = 1
		with open('savedLibrary.bib', 'wb') as savedLibrary:
			savedLibrary.write(file.content)
	except:
		# Otherwise set flag for failed download. (Will use last saved bib file)
		connectionStatus = 0
	
	# Parse the bib file.
	with open('savedLibrary.bib', 'rt') as bibFile:
		textBibData = bibFile.readlines()
	# For some reason, reading strings and parsing must be done separately
	with open('savedLibrary.bib', 'rt') as bibFile:
		parsedBibData = bibtexparser.load(bibFile)
		allBibData = parsedBibData.entries
	
	# Create a set of all keywords for display.
	keywordsList = {
		y for x in allBibData for y in x.get('keywords', '').split(",")}
	keywordsList = keywordsList - set([''])
	# For indexing reasons, the keywords set is converted to a list
	keywordsList = list(keywordsList)
	
	# Format cite keys, authors, and titles in a list for display
	allDisplayEntries = ['{:25}'.format('KEY: ' + x['ID']) +
											 '{}'.format('AUTHOR(S): ' + x['author'])[:50] + '\n' +
											 'TITLE: ' + x['title']
											 for x in allBibData]
	
	# Store the above data in a bibInfoData class
	currentlyShowing = bibInfoData(allDisplayEntries, allBibData)


class bibInfoData:
	""" Define class that restricts data by search terms: """
	""" 'Entries' variables are formatted strings for display. 'bibData' variables
	are dictionary lists of all entries """
	def __init__(self, allEntries, allbibData):
		# allEntries and allBibData are never modified by class methods
		self.allEntries = allEntries
		self.allBibData = allbibData
		
		self.reset_filter()
	
	def reset_filter(self):
		""" bibInfoData.reset_filter sets all other variables to their defaults """
		# Entries that survive just the search filter
		self.searchFilterEntries = self.allEntries
		self.searchFilterBibData = self.allBibData
		
		# Entries that survive both search and keyword filters and are displayed
		self.displayEntries = self.allEntries
		self.displayBibData = self.allBibData
		
		# Keyword currently being used to filter
		self.currentKeyword = ''
		
	def restrict_by_search(self, searchTerms):
		""" bibInfoData.restrict_by_search takes as input a list of search terms and
		finds all entries (from those surviving the keyword filter) that contain a
		one of the terms, and sets those to be displayed """
		searchIndices = []
		# Search all entries
		for term in searchTerms:
			for index in range(len(self.allBibData)):
				for key, value in self.allBibData[index].items():
					if str.lower(term) in str.lower(value):
						searchIndices.append(index)
		searchIndices = set(searchIndices)
		
		# Store entries containing search terms
		self.searchFilterEntries = [self.allEntries[i] for i in searchIndices]
		self.searchFilterBibData = [self.allBibData[i] for i in searchIndices]
		
		if self.currentKeyword == '':
			# If no keyword filter is active display search filtered results
			self.displayEntries = self.searchFilterEntries
			self.displayBibData = self.searchFilterBibData
		else:
			# Otherwise, rerun keyword filter with only the search-filtered results
			self.restrict_by_keyword(self.currentKeyword)
		return
		
	def restrict_by_keyword(self, keyword):
		""" bibInfoData.restrict_by_keyword takes a single keyword as input and
		finds all entries (from those surviving the search filter) that fit the
		keyword, and sets those to be displayed """
		# Set the current keyword. This is used by restrict_by_search
		self.currentKeyword = keyword
		keywordIndices = []
		# Search only entries filtered by the search terms
		for index in range(len(self.searchFilterBibData)):
			try:
				if keyword in self.searchFilterBibData[index]['keywords'].split(','):
					keywordIndices.append(index)
			except:
				continue
		keywordIndices = set(keywordIndices)
		
		# Store entries with keyword and set to be displayed.
		self.displayEntries = [self.searchFilterEntries[i] for i in keywordIndices]
		self.displayBibData = [self.searchFilterBibData[i] for i in keywordIndices]
		return


""" Define functions associated with gui: """


def initial_ui_setup():
	""" initial_ui_setup sets the ui elements up at start according to the
	connectStatus flag (whether the bib file was successfully downloaded) """
	global v, connectionStatus
	
	if connectionStatus == 0:
		# If Dropbox connect failed, show message and retry button.
		# Disable refresh button
		v['noConnectionLabel'].font = ('<system>', 15)
		v['noConnectionLabel'].text = \
			'Failed to connect to Dropbox. Using saved local file. Editing disabled.'
		v['noConnectionLabel'].background_color = "ffffff"
		v['buttonRetryConnect'].enabled = 1
		v['buttonRetryConnect'].hidden = 0
		
		v['buttonRefresh'].enabled = 0
		v['buttonRefresh'].hidden = 1

	else:
		# Otherwise, hide the try button, leave other features enables
		v['buttonRetryConnect'].enabled = 0
		v['buttonRetryConnect'].hidden = 1
	
	# Hide the window that is used for viewing full bib entries.
	v['bibViewWindow'].hidden = 1
	v['bibViewWindow']['bibDisplay'].editable = 0
	v['bibViewWindow']['buttonSaveBib'].enabled = 0
	v['bibViewWindow']['buttonCloseBib'].enabled = 0
	return
	
	
def fill_keywords_menu(keywords):
	""" fill_keywords_menu takes a list of kewords and populates the keywords
	menu """
	keywordsData = ui.ListDataSource(keywords)
	keywordsData.delete_enabled = 0
	keywordsData.move_enabled = 0
	keywordsData.font = ('Courier', 12)
	v['tableKeywords'].data_source = keywordsData
	v['tableKeywords'].reload()
	return
	

def fill_entries_menu(entries):
	""" fill_entries_menu populates the main entries table/menu with the list
	passed to it """
	entriesData = ui.ListDataSource(' ')
	entriesData.delete_enabled = 0
	entriesData.move_enabled = 0
	entriesData.number_of_lines = 2
	entriesData.font = ('Courier', 12)
	entriesData.items = [{'title': x,
												'accessory_type': 'detail_button'}
												for x in entries]
	v['tableEntries'].data_source = entriesData
	v['tableEntries'].reload()
	return
	

def keyword_filter(sender):
	""" keyword_filter is called when the user selects a keyword from the keyword
	menu. It calls the bibInfoData.restrict_by_keyword method """
	global v, currentlyShowing, keywordList
	keywordIndexTuple = v['tableKeywords'].selected_row
	keywordIndex = keywordIndexTuple[1]
	currentlyShowing.restrict_by_keyword(keywordsList[keywordIndex])
	# reload the table
	fill_entries_menu(currentlyShowing.displayEntries)
	return


def search_filter(sender):
	""" search_filter is called when the 'Search' button is pressed. It passes the
	typed search terms to the bibInfoData.restrict_by_search method """
	global v, currentlyShowing
	searchTerms = v['searchField'].text.split(' ')
	currentlyShowing.restrict_by_search(searchTerms)
	# reload the table
	fill_entries_menu(currentlyShowing.displayEntries)
	return
	
	
def clear_filters(sender):
	""" clear_filters is called when the 'Clear Filters' button is pressed. It
	resets all filters, clears the search field, and displays all entries """
	global allDisplayEntries, allBibData, currentlyShowing
	# reset variables in the class
	currentlyShowing.reset_filter()
	# clear the search field
	v['searchField'].text = ''
	# deselect the keyword
	v['tableKeywords'].selected_row = -1
	# reload the table
	fill_entries_menu(currentlyShowing.displayEntries)
	return
	

def refresh_all(sender):
	""" refresh_all is called when the 'Reload' button is pressed. It resets
	everything """
	global v, keywordsList, currentlyShowing
	
	# redownload and parse
	download_and_store()
	# repopulate the tables
	fill_keywords_menu(keywordsList)
	fill_entries_menu(currentlyShowing.displayEntries)
	return


def new_entry(sender):
	""" new_entry is called when the 'New Entry' button is pressed. Eventually it
	will open a window with a form bib entry to allow adding a new entry """
	return


def show_bib(sender):
	""" show_bib is called when an accessory button (the 'i' button) is pressed
	for an entry. It opens a window that displays the bib entry (and allows
	editing). If the program failed to download from Dropbox, the window the bib
	entry will not be editable. """
	global v, connectionStatus, currentlyShowing
	# Show the bib window
	v['bibViewWindow'].bring_to_front()
	v['bibViewWindow'].hidden = 0
	v['bibViewWindow']['buttonCloseBib'].enabled = 1
	
	if connectionStatus == 0:
		# If no connection, show but disable saving changes
		v['bibViewWindow']['bibDisplay'].editable = 0
		v['bibViewWindow']['buttonSaveBib'].enabled = 0
		v['bibViewWindow']['buttonSaveBib'].hidden = 1
		
	else:
		v['bibViewWindow']['bibDisplay'].editable = 1
		v['bibViewWindow']['buttonSaveBib'].enabled = 1
		
	# get the cite key of the tapped entry
	citeKey = currentlyShowing.displayBibData[sender.tapped_accessory_row]['ID']
	# get the bib entry for the key
	v['bibViewWindow']['bibDisplay'].text = return_bibtex(citeKey)
	return
	

def close_bib(sender):
	""" close_bib is called when the bib view window is open and the 'Close'
	button is pressed. It closes that window """
	global v
	v['bibViewWindow'].hidden = 1
	v['bibViewWindow']['buttonCloseBib'].enabled = 0
	v['bibViewWindow']['buttonSaveBib'].enabled = 0
	v['bibViewWindow']['bibDisplay'].editable = 0
	return


def save_bib(sender):
	""" save_bib is called when the bib view window is open and the 'Save Changes'
	button is pressed. It saves and changes made to the bib file and writes them
	to the Dropbox file """
	return


def retry_connect(sender):
	""" retry_connect is called when the 'Retry' button is pressed (only active
	if Dropbox download failed). It just restarts the program... """
	refresh_all(sender)
	return


def load_ui():
	""" load_ui loads the ui at start """
	global v, connectionStatus
	v = ui.load_view('pyBibui')
	initial_ui_setup()
	v.present('full_screen')
	return
	
	
""" Functions auxiliary to interface stuff: """


def return_bibtex(key):
	""" return_bibtex takes a cite key as input and returns the string of its
	associated bibtex entry """
	global textBibData
	reKey = re.compile(key)
	bibLines = []
	keep_printing = False
	for line in textBibData:
		if reKey.findall(line):
			# Beginning of an entry
			keep_printing = True

		if line.strip() == '}':
			if keep_printing:
				bibLines.append(line)
				# End of an entry -- should be the one which began earlier
				keep_printing = False

		if keep_printing:
			# The intermediate lines
			bibLines.append(line)

	bibEntry = "".join(bibLines)
	return bibEntry


""" Launch """
if __name__ == '__main__':
	initial_load()
