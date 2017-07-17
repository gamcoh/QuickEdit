import sublime
import sublime_plugin

import re
import os

class QuickEditCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		# getting the current line 
		curLine    = self.view.sel()[0]
		curLine    = self.view.line(curLine)
		curLineTxt = self.view.substr(curLine)
		
		# getting the first tag if the current line
		firstTag = re.findall('^[^<]*<(.*?)>', curLineTxt)[0]
		
		# search for the tag name
		tagName = re.findall('^([a-zA-Z]+)', firstTag)[0]
		if not tagName:
			self.showError('Impossible de récuperer la balise')
			return False

		# first for all the class names
		className = re.findall('class="(.*?)"', firstTag)[0].split(' ')
		idName = re.findall('id="(.*?)"', firstTag)
		if idName:
			idName = idName[0]

		# first of all we search if the file contains 
		# a style tag with attributs in it
		styleTags = self.view.find_all('<style.*?>')
		
		# we search for links about style sheet css code
		# in this project
		internCssLinks = self.view.find_all('<link[^>]+ href="(?!http).*?".*?>')
		
		# searching for external links
		externCssLinks = self.view.find_all('<link[^>]+ href="http.*?".*?>')

		# init
		self.stylesFound = []

		# searching through all the css style if there are attributs
		# 1 - search in current view style 
		if styleTags:
			# for every class name found for this tag
			# we are gonna found the correspondant attributs
			if className:
				for c in className:
					cssCodes = self.view.find_all('(?s).%s {.*?}' % c)
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
				cwd = sublime.active_window().folders()[-1]
				code = open(cwd+'/'+code).read()
				# for every class name found for this tag
				# we are gonna found the correspondant attributs
				if className:
					for c in className:
						cssCodes = re.findall('(?s).%s {.*?}' % c, code)
						if cssCodes:
							for css in cssCodes:
								self.stylesFound.append({'code': css, 'file': file})

		# Last - show the phantom with the formated css code
		self.formatCode()


	def formatCode(self):
		reportHtml=""
		for code in self.stylesFound:
			# adding the file name
			if code['file'] == 'self':
				reportHtml += '<p class="files"><em>in this file</em>, at line : <a href="line-{line}">{line}</a></p>'.format(line=code['line'])
			else:
				reportHtml += '<p class="files"><em>in %s</em></p>' % (code['file'])

			reportHtml += code['code']

		if not reportHtml:
			return False

		# reportHtml = reportHtml.replace(";", ";</")
		reportHtml = re.sub(r'\n|\t', '', reportHtml)
		reportHtml = re.sub(r'([a-zA-Z0-9_. ]+) {', '<p class="className">\g<1> <b>{</b></p>', reportHtml)
		reportHtml = re.sub(r'}', '<p class="className"><b>}</b></p>', reportHtml)
		reportHtml = re.sub(r'([a-zA-Z_-]+): ([a-zA-Z0-9_-]+);', '<p class="attributs"><em>\g<1></em>: <b>\g<2></b>;</p>', reportHtml)

		# load css, and html ui
		css = sublime.load_resource('Packages/QuickEdit/resources/ui.css')
		html = sublime.load_resource('Packages/QuickEdit/resources/report.html').format(css=css, html=reportHtml)

		self.view.erase_phantoms('quick_edit')
		self.view.add_phantom("quick_edit", self.view.sel()[0], html, sublime.LAYOUT_BLOCK, self.click)


	# when the user click on one of the phantom action
	def click(self, href):
		if 'line-' in href:
			self.view.run_command('goto_line', args={'line': href.split('-')[1]})
			self.view.erase_phantoms("quick_edit")
		elif href == 'close':
			self.view.erase_phantoms('quick_edit')





