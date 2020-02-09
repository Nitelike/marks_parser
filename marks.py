import requests
from lxml import html
import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label 

const_login = ""
const_password = ""


class MarksApp(App):
	box = BoxLayout(orientation="vertical", padding=30)
	def build(self, *args):
		self.box.clear_widgets()
		self.login = TextInput(hint_text="Логин")
		self.password = TextInput(hint_text="Пароль", password=True)
		self.button = Button(text="Отправить")

		self.button.bind(on_press=self.show_children)

		self.box.add_widget(self.login)
		self.box.add_widget(self.password)
		self.box.add_widget(self.button)

		return self.box

	def show_marks(self, button):
		self.box.clear_widgets()

		marks = self.parse(const_login, const_password, button.id)
		for i in marks:
			row = BoxLayout(orientation="horizontal")
			s1 = ""
			s2 = ""
			s3 = ""

			s1 = i
			for j in marks[i][0]:
				s2 += str(j) + " "
			s3 = str(marks[i][1][0])

			title = Label(text=s1)
			m1 = Label(text=s2)
			m2 = Label(text=s3)

			row.add_widget(title)
			row.add_widget(m1)
			row.add_widget(m2)
			self.box.add_widget(row)

		row = BoxLayout(orientation="horizontal")
		back = Button(text="Назад")
		back.bind(on_press=self.build)
		row.add_widget(back)
		self.box.add_widget(row)


	def show_children(self, btn):
		global const_login
		global const_password
		const_login = self.login.text
		const_password = self.password.text

		children = self.getChildren(const_login, const_password)
		
		self.box.remove_widget(self.login)
		self.box.remove_widget(self.password)
		self.box.remove_widget(self.button)

		for i in children:
			self.box.add_widget(Button(text=children[i], id=i, on_press=self.show_marks))	

		
	def days_in_month(self, month, year):
		if month == 9:
			return 31
		elif month % 2 == 0 and month != 9 and month != 2:
			return 30
		elif (month == 2):
			if year % 4 != 0 or year % 100 == 0 and year % 400 != 0:
				return 28
			else:
				return 29
		else:
			return 31



	def parse(self, login, password, pupil_id):
		session_requests = requests.session()

		login_url = "https://schools.by/login"
		result = session_requests.get(login_url)

		tree = html.fromstring(result.text)
		authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

		payload = {
			"username": login, 
			"password": password, 
			"csrfmiddlewaretoken": authenticity_token
		}

		result = session_requests.post(
			login_url, 
			data = payload, 
			headers = dict(referer=login_url)
		)

		url = 'https://schools.by/'
		result = session_requests.get(
			url, 
			headers = dict(referer = url)
		)

		tree = html.fromstring(result.content)
		parent_url = tree.xpath("//div[@class='h-auth']/ul[@class='t-menu']/li[@class='t-menu-item']/a[@class='t-menu-link']")[0].attrib['href']

		school_url = parent_url[:parent_url.find('/parent/')+1]
		
		diary_url = school_url + "/pupil/" + pupil_id + "/dnevnik"

		result = session_requests.get(
			diary_url, 
			headers = dict(referer = diary_url)
		)

		tree = html.fromstring(result.content)
		quarter = tree.xpath("//a[@class='current']/@src")[0]
		quarter = str(quarter[len(quarter) - 2:])

		diary_url += "/quarter/"

		now = datetime.datetime.now()

		mode = int(quarter) - 25 - (now.year - 2018) * 7;
		if mode <= 0:
			mode += 7

		year = now.year
		year2 = year
		month = 1
		month2 = 0
		day = 1
		d = 1
		d2 = 1

		if mode == 1:
			year = now.year
			year2 = year
			month = 9
			month2 = 10
			day = 1
			day2 = self.days_in_month(month2, year2)
		elif mode == 2:
			year = now.year
			year2 = year
			month = 11
			month2 = 12
			day = 1
			day2 = self.days_in_month(month2, year2)
		elif mode == 3:
			year = now.year
			year2 = year
			month = 1
			month2 = 3
			day = 1
			day2 = self.days_in_month(month2, year2)
		elif mode == 4:
			year = now.year
			year2 = year
			month = 4
			month2 = 5
			day = 1
			day2 = self.days_in_month(month2, year2)
		elif mode == 5:
			year = now.year
			year2 = year
			month = 9
			month2 = 11
			day = 1
			day2 = self.days_in_month(month2, year2)
		elif mode == 6:
			month = 12
			month2 = 14
			day = 1	

			if now.month < 12:
				year = now.year - 1
				year2 = now.year	
			else:
				year = now.year
				year2 = year + 1

			day2 = self.days_in_month(month2 - 12, year2)
		elif mode == 7:
			year = now.year
			year2 = year
			month = 3
			month2 = 5
			day = 1
			day2 = self.days_in_month(month2, year2)

		qmarks = {}
		result_marks_url = school_url + "/pupil/" + pupil_id + "/dnevnik/last-page"

		result = session_requests.get(
			result_marks_url, 
			headers = dict(referer = result_marks_url)
		)

		tree = html.fromstring(result.text)
		tr_list = tree.xpath("//table[@class='itable mtable']/tbody/tr[@class='marks']")
		names = tree.xpath("//table[@class='itable ltable']/tbody/tr")

		col = 1
		if mode < 5:
			col = mode - 1
		else:
			col = mode - 5

		for i in range(0, len(tr_list)):
			name = names[i].xpath(".//td/p/a/text()")[0]
			name = ' '.join(name.split())
			mark = tr_list[i].xpath(".//td[@class='qmark']")[col].text_content()
			if (str(mark) != ''):
				qmarks[name] = int(mark)
			else:
				qmarks[name] = '-'		

		subjects = {}
		for m in range(month, month2 + 1):
			y = year

			if m > 12:
				m -= 12

			if m < 7:
				y = year2

			if m == month:
				d = day
			else:
				d = 1

			if m == month2:
				d2 = day2
			else:
				d2 = self.days_in_month(m, y)

			for w in range(d, d2 + 1, 7):
				url = diary_url + quarter + "/week/" + str(y) + "-" + str(int(m / 10)) + str(int(m % 10)) + "-" + str(int(w / 10)) + str(int(w % 10))

				result = session_requests.get(
					url, 
					headers = dict(referer = url)
				)
				tree = html.fromstring(result.text)
				for d in range(w, w + 8):
					if (d < self.days_in_month(month, y)):
						table = "//table[@id='db_table_" + str(int(d / 10)) + str(int(d % 10)) + "." + str(int(m / 10)) + str(int(m % 10)) + "." + str(int(y / 10) % 10) + str(y % 10) + "']"
						lessons = tree.xpath(table + "/tbody/tr")
						for lesson in lessons:
							name = lesson.xpath(".//td[@class='lesson ']/span/text()")[0]
							name = ' '.join(name.split())[3:]
							mark = lesson.xpath(".//td[@class='mark']/div/strong/text()")
							if len(mark) > 0:
								mark = mark[0]
							else:
								mark = 0
							if name != False:
								if name not in subjects and mark != 0:
									subjects[name] = [int(mark)]
								elif name not in subjects and mark == 0:
									subjects[name] = []
								else:
									if mark != 0 and '/' not in mark:
										subjects[name].append(int(mark))
									elif mark != 0 and '/' in mark:
										pos = mark.find('/')								
										subjects[name].append(int(mark[:pos]))
										subjects[name].append(int(mark[pos + 1:]))

		marks = {}

		for subject in subjects:
			if len(subjects[subject]) != 0 and subject != '':
				marks[subject] = [subjects[subject], [round(sum(subjects[subject]) / len(subjects[subject]), 2)], [qmarks[subject]]]
			elif subject != '':
				marks[subject] = [["-"], ["-"], [qmarks[subject]]]

		return marks



	def getChildren(self, login, password):
		session_requests = requests.session()

		login_url = "https://schools.by/login"
		result = session_requests.get(login_url)

		tree = html.fromstring(result.text)
		authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

		payload = {
			"username": login, 
			"password": password, 
			"csrfmiddlewaretoken": authenticity_token
		}

		result = session_requests.post(
			login_url, 
			data = payload, 
			headers = dict(referer=login_url)
		)

		url = 'https://schools.by/'
		result = session_requests.get(
			url, 
			headers = dict(referer = url)
		)

		tree = html.fromstring(result.content)
		parent_url = tree.xpath("//a[@class='t-menu-link']")[0].attrib['href']

		result = session_requests.get(
			parent_url, 
			headers = dict(referer = parent_url)
		)

		tree = html.fromstring(result.content)
		children_names = tree.xpath("//a[@class='user_type_1']/text()")
		children_links = tree.xpath("//ul[@id='parent-pupils-tabs-menu']/li/a")

		children = {}

		for i in range(len(children_links)):
			children[str(children_links[i].attrib['href'][7:])] = children_names[i]

		return children

if __name__ == "__main__":
	MarksApp().run()

