import sublime
import sublime_plugin

import re
import os

# from bs4 import BeautifulSoup

class QuickEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# init
		self.aErrors = []
		self.QuickEditSetting = sublime.load_settings('QuickEdit.sublime-settings')

		# getting the current line 
		self.curRegion  = self.view.sel()[0]
		self.curLine    = self.view.line(self.curRegion)
		self.curLineTxt = self.view.substr(self.curLine)

		# getting the current scope
		scope = self.view.scope_name(self.curRegion.a)
		if 'source.php' in scope and 'variable.other.php' in scope:
			self.scope = 'php_variable'
			# if the scope is php_variable
			# we search in the same file (for now)
			# where was the current variable defined.
			# Also instead of taking the all line 
			# we just take the wone world under mouse 
			self.curLineTxt = self.view.substr(self.view.word(self.view.sel()[0]))
			self.searchForVar();
		elif 'source.php' in scope and ('meta.function-call.php' in scope or 'variable.function.php' in scope):
			self.scope = 'php_function'
			# if the scope is php_function
			# we search in the current view (for now)
			# where did this function was defined
			self.curLineTxt = self.view.substr(self.view.word(self.view.sel()[0]))
			self.searchForFunction()
		else:
			self.scope = 'html_css'
			# if the scope is html_css we 
			# search for the class names
			# the id names and the styles for them 
			self.searchForStyles()


	########################################################################
	# Search for the class name, the id,
	# and the correspondant styles
	# in different files across the folder
	########################################################################
	def searchForStyles(self):
		# getting the first tag if the current line
		firstTag = re.search('^[^<]*<(.*?)>', self.curLineTxt).group(1)
		
		# search for the tag name
		tagName = re.search('^([a-zA-Z]+)', firstTag).group(1)
		if not tagName:
			self.showError('Impossible de récuperer la balise')
			return False

		# first for all the class names
		className = re.findall('class="(.*?)"', firstTag)
		if className:
			className = className[0].split(' ')
		else:
			self.aErrors.append('Could find any class name in this tag')

		# search for an id
		idName = re.findall('id="(.*?)"', firstTag)
		if idName:
			idName = idName[0]

		# first of all we search if the file contains 
		# a style tag with attributs in it
		styleTags = self.view.find_all('<style.*?>')
		
		# we search for links about style sheet css code
		# in this project
		internCssLinks = self.view.find_all('<link[^>]+ href="(?!http).*?\.css".*?>')
		
		# searching for external links
		externCssLinks = self.view.find_all('<link[^>]+ href="http.*?\.css".*?>')

		# init
		self.stylesFound = []

		# searching through all the css style if there are attributs
		# 1 - search in current view style 
		if styleTags:
			# for every class name found for this tag
			# we are gonna found the correspondant attributs
			if className:
				for c in className:
					cssCodes = self.view.find_all('(?s)[#a-zA-Z0-9 _.-]*.%s\s?{.*?}' % c)
					if cssCodes:
						for code in cssCodes:
							self.stylesFound.append({'code': self.view.substr(code), 'line': str(self.view.rowcol(code.a)[0] + 1), 'file': 'self'})
		# 2 - search in internal css style sheets
		if internCssLinks:
			links = [self.view.substr(link) for link in internCssLinks]
			codeFiles = [re.search('''href=("|')(.*?)('|")''', link).group(2) for link in links]
			# loop on all the css file included
			for code in codeFiles:
				file = code
				cwd = sublime.active_window().folders()[0]
				try:
					with open(os.path.join(cwd, code)) as link_file:
						code = link_file.read()
				except FileNotFoundError as e:
					self.aErrors.append('Could not find the file : ' + str(e).split(':')[1])
				# for every class name found for this tag
				# we are gonna found the correspondant attributs
				if className:
					for c in className:
						cssCodes = re.findall('(?s)[#a-zA-Z0-9 _.-]*.%s\s?{.*?}' % c, code)
						if cssCodes:
							for css in cssCodes:
								self.stylesFound.append({'code': css, 'file': file})
		self.formatCode()


	########################################################################
	# Search for were the variable was defined
	########################################################################
	def searchForVar(self):
		# search for the varibale definition
		variableFormatted = '\$' + self.curLineTxt
		varsFoundLine = self.view.find_all('(?!{0}\s?==)({0}\s?=.*)'.format(variableFormatted))
		
		# if the definition were not found
		if not varsFoundLine:
			self.aErrors.append('Could not find the definition of %s in this file' % variableFormatted.replace('\$', '$'))

		# if multiple var were found
		if len(varsFoundLine) > 1:
			self.varsFound = {'line': str(self.view.rowcol(varsFoundLine[-1].a)[0] + 1), 'code': self.view.substr(varsFoundLine[-1])}
		else:
			self.varsFound = {'line': str(self.view.rowcol(varsFoundLine[0].a)[0] + 1), 'code': self.view.substr(varsFoundLine[0])}

		self.formatCodeVar()


	########################################################################
	# Search for were the function was defined
	########################################################################
	def searchForFunction(self):
		# search for the varibale definition
		functionFormatted = 'function ' + self.curLineTxt
		functionsFound = self.view.find_all('(.*{}.*)'.format(functionFormatted))

		print(functionFormatted)
		
		# if the definition were not found
		if not functionsFound:
			self.aErrors.append('Could not find the definition of %s in this file' % functionFormatted)
			self.formatCodeFunction()
			return False

		# if multiple var were found
		if len(functionsFound) > 1:
			self.functionFound = {'line': str(self.view.rowcol(functionsFound[-1].a)[0] + 1), 'code': self.view.substr(functionsFound[-1])}
		else:
			self.functionFound = {'line': str(self.view.rowcol(functionsFound[0].a)[0] + 1), 'code': self.view.substr(functionsFound[0])}

		self.formatCodeFunction()

	########################################################################
	# format the code for the vars
	########################################################################
	def formatCodeVar(self):
		reportHtml = '<div class="var">'
		reportHtml += '<p class="files"><em>in this file, at line : </em><a href="line-{line}">{line}</a></p>'.format(line=self.varsFound['line'])

		# format the code for a better syntax coloration
		reportHtmlContent = re.sub('(\$|=|new|->)', '<p class="monokai_red">\g<1></p>', self.varsFound['code'])
		reportHtmlContent = re.sub('(class)(;|,)', '<p class="monokai_blue">\g<1></p>\g<2>', reportHtmlContent)
		reportHtmlContent = re.sub('(\[| |=|>)([0-9]+)(\]| |;|,)', '\g<1><p class="monokai_int">\g<2></p>\g<3>', reportHtmlContent)
		# print(reportHtmlContent)
		
		reportHtml += reportHtmlContent
		reportHtml += '</div>'

		# load the font
		settings = sublime.load_settings('Preferences.sublime-settings')
		font = ''
		if settings.has('font_face'):
			font = '"%s",' % settings.get('font_face')

		# getting the errors that occured during the execution
		htmlErrors = ''
		if self.QuickEditSetting.get('show_errors'):
			for e in self.aErrors:
				htmlErrors += '<p class="error">• %s</p>' % e

			# if errors were found 
			if htmlErrors:
				htmlErrors = '<div class="panel panel-error mt20"><div class="panel-header">Errors that occured during the search</div><div class="panel-body">{errors}</div></div>'.format(errors=htmlErrors)

		# load css, and html ui
		css = sublime.load_resource('Packages/QuickEdit/resources/ui.css').replace('@@font', font)
		html = sublime.load_resource('Packages/QuickEdit/resources/report.html').format(css=css, html=reportHtml, errors=htmlErrors)

		self.view.erase_phantoms('quick_edit')
		self.view.add_phantom("quick_edit", self.view.sel()[0], html, sublime.LAYOUT_BLOCK, self.click)

	########################################################################
	# format the code for the functions
	########################################################################
	def formatCodeFunction(self):
		try:
			reportHtml = '<div class="function">'
			reportHtml += '<p class="files"><em>in this file, at line : </em><a href="line-{line}">{line}</a></p>'.format(line=self.functionFound['line'])

			# format the code for a better syntax coloration
			reportHtmlContent = re.sub('(private|public|protected|return)', '<p class="monokai_red">\g<1></p>', self.functionFound['code'])
			reportHtmlContent = re.sub('(function)', '<p class="monokai_blue"><em>\g<1></em></p>', reportHtmlContent)
			reportHtmlContent = re.sub('(function</em></p> )([a-zA-Z0-9_]+)( ?\()', '\g<1><p class="monokai_green">\g<2></p>\g<3>', reportHtmlContent)
			reportHtmlContent = re.sub('(function</em></p> <p class="monokai_green">customizeMessage</p>\()(.*)(\))', '\g<1><p class="monokai_params"><em>\g<2></em></p>\g<3>', reportHtmlContent)
			reportHtmlContent = re.sub('(\{.*)(\$)(.*\})', '\g<1><p class="monokai_red"><em>\g<2></em></p>\g<3>', reportHtmlContent)
			reportHtmlContent = re.sub('(\{.*)(->)(.*\})', '\g<1><p class="monokai_red"><em>\g<2></em></p>\g<3>', reportHtmlContent)
			
			reportHtml += reportHtmlContent
			reportHtml += '</div>'
		except AttributeError:
			print('[Errno 2] Function not found')

		# load the font
		settings = sublime.load_settings('Preferences.sublime-settings')
		font = ''
		if settings.has('font_face'):
			font = '"%s",' % settings.get('font_face')

		# getting the errors that occured during the execution
		htmlErrors = ''
		if self.QuickEditSetting.get('show_errors'):
			for e in self.aErrors:
				htmlErrors += '<p class="error">• %s</p>' % e

			# if errors were found 
			if htmlErrors:
				htmlErrors = '<div class="panel panel-error mt20"><div class="panel-header">Errors that occured during the search</div><div class="panel-body">{errors}</div></div>'.format(errors=htmlErrors)

		# load css, and html ui
		css = sublime.load_resource('Packages/QuickEdit/resources/ui.css').replace('@@font', font)
		html = sublime.load_resource('Packages/QuickEdit/resources/report.html').format(css=css, html=reportHtml, errors=htmlErrors)

		self.view.erase_phantoms('quick_edit')
		self.view.add_phantom("quick_edit", self.view.sel()[0], html, sublime.LAYOUT_BLOCK, self.click)


	########################################################################
	# format the css code in order to show 
	# it in a phantom report modal
	########################################################################
	def formatCode(self):
		reportHtml=""
		for code in self.stylesFound:
			# adding the file name
			if code['file'] == 'self':
				reportHtml += '<p class="files"><em>in this file</em>, at line : <a href="line-{line}">{line}</a></p>'.format(line=code['line'])
			else:
				reportHtml += '<p class="files"><em>in %s</em></p>' % (code['file'])

			reportHtml += code['code']

		# no css style were found
		if not reportHtml:
			self.aErrors.append('Could not find any css style')

		# put minihtml tag and class name 
		# in order to stylize the css
		reportHtml = re.sub(r'\n|\t', '', reportHtml)

		# found all the pre-brackets code
		pre_brackets = re.findall(r'([#a-zA-Z0-9_. ]+)(\s?){', reportHtml)
		for r in pre_brackets:
			# for all the pre-brackets code we search for tag names, id,
			# and class name in order to format them
			formattedCode = re.sub(r'([#a-zA-Z0-9_.-]+)', '<p class="tagName">\g<1></p>', r[0])
			formattedCode = re.sub(r'<p class="tagName">(\.[a-zA-Z0-9_.-]+)<\/p>', '<p class="className">\g<1></p>', formattedCode)
			formattedCode = re.sub(r'<p class="tagName">(#[#a-zA-Z0-9_-]+)<\/p>', '<p class="idName">\g<1></p>', formattedCode)
			reportHtml = re.sub(r[0], formattedCode, reportHtml)

		reportHtml = re.sub(r'}', '<p class="className"><b>}</b></p>', reportHtml)
		reportHtml = re.sub(r'([a-zA-Z_-]+): ([a-zA-Z0-9_-]+);', '<p class="attributs"><em>\g<1></em>: <b>\g<2></b>;</p>', reportHtml)

		# load the font
		settings = sublime.load_settings('Preferences.sublime-settings')
		font = ''
		if settings.has('font_face'):
			font = '"%s",' % settings.get('font_face')

		# getting the errors that occured during the execution
		htmlErrors = ''
		if self.QuickEditSetting.get('show_errors'):
			for e in self.aErrors:
				htmlErrors += '<p class="error">• %s</p>' % e

			# if errors were found 
			if htmlErrors:
				htmlErrors = '<div class="panel panel-error mt20"><div class="panel-header">Errors that occured during the search</div><div class="panel-body">{errors}</div></div>'.format(errors=htmlErrors)

		# load css, and html ui
		css = sublime.load_resource('Packages/QuickEdit/resources/ui.css').replace('@@font', font)
		html = sublime.load_resource('Packages/QuickEdit/resources/report.html').format(css=css, html=reportHtml, errors=htmlErrors)

		self.view.erase_phantoms('quick_edit')
		self.view.add_phantom("quick_edit", self.view.sel()[0], html, sublime.LAYOUT_BLOCK, self.click)


	# when the user click on one of the phantom action
	def click(self, href):
		# if the user click on a line, we use the goto function
		if 'line-' in href:
			self.view.run_command('goto_line', args={'line': href.split('-')[1]})
			self.view.erase_phantoms("quick_edit")
		# closing the phantom
		elif href == 'close':
			self.view.erase_phantoms('quick_edit')





