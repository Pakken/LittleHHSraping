import urllib.request
import csv
import sys
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from pandas import date_range,Series,DataFrame,read_csv, qcut
from pandas.tools.plotting import radviz,scatter_matrix,bootstrap_plot,parallel_coordinates
from numpy.random import randn
from pylab import *
import brewer2mpl
from matplotlib import rcParams
import sqlite3 as lite

dark2_colors = brewer2mpl.get_map('Dark2', 'Qualitative', 7).mpl_colors

rcParams['figure.figsize'] = (10, 6)
rcParams['figure.dpi'] = 150
rcParams['axes.color_cycle'] = dark2_colors
rcParams['lines.linewidth'] = 2
rcParams['axes.facecolor'] = 'white'
rcParams['font.size'] = 14
rcParams['patch.edgecolor'] = 'white'
rcParams['patch.facecolor'] = dark2_colors[0]
rcParams['font.family'] = 'StixGeneral'

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

# Функция записи результатов в csv файл 
def write_csv(lvac,path):
	with open(path,'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow('Требования')
        
		for vac in lvac:
		    writer.writerow(vac)

# Функция получения количества страниц после поиска вакансий            
def get_page_count(html):
    
	soup = BeautifulSoup(html, 'html.parser')
	page_count_text = soup.find('div', class_ = 'search-result-counter').text  
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
	con = lite.connect('hh_db.sqlite')
	cur = con.cursor()
	word_key = 0

	cur.execute('CREATE TABLE trebov (entry_id integer PRIMARY KEY,word text,treb_id integer)')
	cur.execute('CREATE TABLE slovar (word_id integer PRIMARY KEY,word text UNIQUE')
	for i in range(len(cld)):
		for j in cld[i]:
			ey = '("' + j + '",' + str(i+1) + ')'
			cur.execute('INSERT INTO trebov (word,treb_id) VALUES' + '("' + j + '",' + str(i+1) + ')')
			cur.execute('INSERT OR IGNORE INTO slovar (word) VALUES' + '("' + j + '")')
			word_key += 1
	con.commit()
	con.close()

# Функция подсчета слов 
	con = lite.connect(hh_db.sqlite)
	cur = con.cursor()
	
	cur.execute(
	
	
	
# Функция графического вывода полученных данных
def remove_border(axes=None, top=False, right=False, left=True, bottom=True):
	ax = axes or plt.gca()
	ax.spines['top'].set_visible(top)
	ax.spines['right'].set_visible(right)
	ax.spines['left'].set_visible(left)
	ax.spines['bottom'].set_visible(bottom)
    	
	#turn off all ticks
	ax.yaxis.set_ticks_position('none')
	ax.xaxis.set_ticks_position('none')

	#now re-enable visibles
	if top:
		ax.xaxis.tick_top()
	if bottom:
		ax.xaxis.tick_bottom()
	if left:
		ax.yaxis.tick_left()
	if right:
		ax.yaxis.tick_right()

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
	
					
#	cld = datacl(lvac)
#	pairs = fintr(cld)
#
#	for i in pairs:
#		city.append(i[0])
#		change.append(i[1])

	grad = DataFrame({'change' : change, 'city': city})
 
	plt.figure(figsize=(3, 8))
 
	change = grad.change[grad.change > 0]
	city = grad.city[grad.change > 0]
	pos = np.arange(len(change))
 
	plt.title('1995-2005 Change in HS graduation rate')
	plt.barh(pos, change)
 
	#add the numbers to the side of each bar
	for p, c, ch in zip(pos, city, change):
    		plt.annotate(str(ch), xy=(ch + 1, p + .5), va='center')
 
	#cutomize ticks
	ticks = plt.yticks(pos + .5, city)
	xt = plt.xticks()[0]
	plt.xticks(xt, [' '] * len(xt))
 
	#minimize chartjunk
	remove_border(left=False, bottom=False)
	plt.grid(axis = 'x', color ='white', linestyle='-')
 
	#set plot limits
	"""plt.ylim(pos.max(), pos.min() - 1)
	plt.xlim(0, 30)"""	
			
	write_csv(pairs,path)

	#for i in cld:
	#	print(i)

	#print(len(lvac))

if __name__ == '__main__':
    main()

