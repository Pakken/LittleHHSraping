import urllib.request
import math
import sys
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sqlite3

# Функция для чтения вакасии из командной строки
def get_vac():
	print('Введите желаемую вакансию : ')
	search_vac = sys.stdin.readline()
	search_vac_tr = urllib.parse.quote(search_vac)
	url = 'https://hh.ru/search/vacancy?items_on_page=100&clusters=true&text=%D0%91%D1%83%D1%85%D0%B3%D0%B0%D0%BB%D1%82%D0%B5%D1%80&enable_snippets=true&no_magic=true&search_field=name&page=0'
	url1 = url.replace('%D0%91%D1%83%D1%85%D0%B3%D0%B0%D0%BB%D1%82%D0%B5%D1%80',search_vac_tr)
	return url1

# Функция получения html кода страницы 
def get_html(url):
	response = urllib.request.urlopen(url)
	return response.read()

# Функция получения количества страниц после поиска вакансий            
def get_page_count(html):
    
	soup = BeautifulSoup(html, 'html.parser')
	page_count_text = soup.find('h1', class_ = 'header').text  
	page_count = ''
	for i in page_count_text:
		if i.isdigit():
			page_count += i    
	page_count = int(page_count) // 100 + 1 
        
	return page_count

# Функция парсинга отдельной вакансии из списка
def parse_vac(html):
	vacdes = []
	     
	soup = BeautifulSoup(html,"html.parser")
	zag = soup.find(text = ['Требования:','Требования','Требуемые навыки:'])
	if zag != None:
		dannie = zag.findNext('ul')
		if dannie != None:
			vacdes = [i.text for i in dannie.find_all('li')]
            
	return vacdes 

# Функция парсинга результатов поиска по вакансии    
def parse(html):
	cl1 ='bloko-gap bloko-gap_top'
	cl2 = 'search-result-description'
	cl3 = 'search-result-item__snippet'
    
	vacd =[]
    
	soup = BeautifulSoup(html,"html.parser")
	dannie = soup.find('div',class_ = cl1)
	for vac in dannie.find_all('div', class_ = cl2):
		vac_url = vac.a.get('href')
		duties = parse_vac(get_html(vac_url))
		if duties != [] :
			for i in duties:
				vacd.append(i)
        
	return vacd

# Функция обработки требований
def datacl(lvac):
	trash = [' ','в','на','по','около','с','под','\n','\t','и','за','этот','его','прочее','его','пр','др','проч','от','-','то','эта','эти','это','чем','чему','через','чтобы','я','то','тоже','только','том']
	punkt = [',','.',':',';','%','/','(',')',"'",'"','-','|','*','+','»','!','«']
	cld = []

	for i in lvac:
		for j in punkt:
			i = i.replace(j,' ',i.count(j)+1)
		cld.append(i.lower().split())

	for i in cld:
		for j in  trash:
			for k in range(i.count(j)):
				i.remove(j)
	for i in cld:
		i.sort()

	cld.sort()

	return cld

# Функция создания базы данных
def cr_db(cld):
	con = sqlite3.connect('hh_db.db')
	cur = con.cursor()

	cur.execute('CREATE TABLE trebov (treb_id integer PRIMARY KEY,treb text)')
	cur.execute('CREATE TABLE slovar (word_id integer PRIMARY KEY, word text UNIQUE)')
	cur.execute('CREATE TABLE results (res_id integer PRIMARY KEY,w1 text,w2 text,w3 text,kolvo integer)')
	
	
	for i in cld:
		temp = ''
		for j in i:
			cur.execute('INSERT OR IGNORE INTO slovar (word) VALUES ("' + j + '")')
			temp += j + ' '
		cur.execute('INSERT INTO trebov (treb) VALUES ("' + temp + '")')
	
	con.commit()
	con.close()

# Функция подсчета слов 
def get_final_res():
	con = sqlite3.connect('hh_db.db')
	cur = con.cursor()
	
	cur.execute('SELECT count(word_id) FROM slovar')
	l = cur.fetchall()[0][0]
	
	for i in range(1,l-1):
		for j in range(i+1,l):
			for k in range(j+1,l+1):
				ey = 'SELECT word FROM slovar WHERE word_id = '
				cur.execute(ey + str(i) + ' UNION ' + ey + str(j) + ' UNION ' + ey + str(k))
				comb = cur.fetchall()
				cur.execute('SELECT count(*) FROM trebov WHERE treb LIKE "%' + comb[0][0] + '''%" AND treb LIKE
				"%''' + comb[1][0] + '%" AND treb LIKE "%' + comb[2][0] + '%"')
				n = cur.fetchall()[0][0]
				cur.execute('INSERT INTO results (w1,w2,w3,kolvo) VALUES ("' + comb[0][0] + '","' + comb[1][0] + '","' + comb[2][0] + '",' + str(n) + ')')
				
	con.commit()
	con.close()
	
# Функция графического вывода полученных данных
def show_final_res():
	n = 10

	plt.style.use('classic')
	mpl.rcParams['lines.linewidth'] = 0.5
	mpl.rcParams['font.size'] = 8		
	
	con = sqlite3.connect('hh_db.db')
	cur = con.cursor()
	
	cur.execute('SELECT w1,w2,w3,kolvo FROM results WHERE kolvo != 0 ORDER BY kolvo DESC LIMIT ' +  str(n))
	res = cur.fetchall()
	
	cur.execute('SELECT max(kolvo) FROM results')
	m = cur.fetchall()[0][0]
	
	y = []
	lx = ()
	ly = ()
	x = [i*500 for i in range(n)]
	
	for i in res:
		y.append(i[3])
		lx += (i[0] + '\n' + i[1] + '\n' + i[2],)
	
	for i in range(m):
		ly += (str(i),)
	
	fig = plt.subplot()

	fig.bar(x,y,align = 'center',tick_label = '',width = 100, color = 'green')
	for _x,_y,t in zip(x,y,lx):
		fig.annotate(t,(_x,_y-0.005*math.fmod(_x,200)),fontsize = 7, ha = 'center',
		xytext = (0,-2),textcoords = 'offset pixels',
		bbox = {'facecolor':'w'})

	plt.savefig('final_results_graf')
	plt.close()
	con.close()
	
# Функция главная
def main():
	
	path = 'vacancy_list.csv'  
	lvac = []
	page_count = 1
	city = []
	change = []	
	
	url = get_vac()

	if page_count > get_page_count(get_html(url)):
		page_count = get_page_count(get_html(url))

	for page in range(0,page_count):
		print('Парсинг %d%%' % (page / page_count * 100))
		lvac.extend(parse(get_html(url.replace('page=0','page=%d' % page))))

	print('Парсинг %d%%' % (100))

	cr_db(datacl(lvac))
	get_final_res()
	show_final_res()		

if __name__ == '__main__':
    main()

