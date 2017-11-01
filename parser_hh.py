import urllib.request
import csv
import sys
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from pandas import date_range,Series,DataFrame,read_csv,qcut
from pandas.tools.plotting import radviz,scatter_matrix,bootstrap_plot,parallel_coordinates
from numpy.random import randn
from pylab import *
import brewer2mpl
from matplotlib import rcParams


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
	trash = [' ','в','на','по','около','с','под','\n','\t','и','за','этот','его','прочее','его','пр','др','проч','от','-']
	punkt = [',','.',':',';','%','#','(',')']
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

# Функция нахождения количества одинаковых требований
def fintr(cld):
	slv = []
	n_sl = []
	for i in cld:
		slv.append(i)

	for i in slv:
		for j in range(slv.count(i)-1):
			slv.remove(i)
	slv.sort()

	for i in slv:
		for j in slv:
			for k in slv:
				c = 0
				for v in cld:
					if i != j and i != k and j !=k:
						if i in v and j in v and k in v:
							c += 1 
				pairs.append([i[0]+' '+j[0]+' '+k[0],c])
	return(pairs)

# Функция графического вывода полученных данных


dark2_colors = brewer2mpl.get_map('Dark2','Qualitative',7).mpl_colors
rcParams['figure.figsize'] = (10,6)
rcParams['figure.dpi'] = 150
rcParams['axes.color_cycle'] = dark2_colors
rcParams['lines.linewidth'] = 2
rcParams['axes.facecolor'] = 'white'
rcParams['font.size'] = 14
rcParams['patch.edgecolor'] = 'white'
rcParams['patch.facecolor'] = dark2_colors[0]
rcParams['font.family'] = 'StixGeneral'

def remove_border(axes=None, top=False, right = False, left = True, bottom = True):
	ax = axes or pls.gca()
	ax.spines['top'].set_visible(top)
	ax.spines['right'].set_visible(right)
	ax.spines['left'].set_visible(left)
	ax.spines['bottom'].set_visible(bottom)
	ax.yaxis.set_ticks_position('none')
	ax.xaxis.set_ticks_position('none')

	if top:
		ax.xaxis.tick_top()
	if bottom:
		ax.xaxis.tick_bottom()
	if left:
		ax.yaxis.tick_left()
	if right:
		ax.yaxis.tick_right()

def drimage(pairs):
	naz = []
	kolvo = []

	for i in pairs:
		naz.append(i[0])
		kolvo.append(i[1])

	grad = DataFrame({'nazvanie' : naz, 'kolvo' : kolvo})

	plt.figure(figsize = (3,8))

	naz = grad.naz[grad.change > 0]
	kolvo = grad.kolvo[grad.change > 0]
	pos = np.arange(len(kolvo))

	plt.title('Список наиболее востребованных умений')
	plt.barh(pos, kolvo)

	for p , n , k in zip(pos, naz, kolvo):
		plt.annotate(str(k), xy = (k + 1, p + .5), va = 'center')

	ticks = plt.yticks(pos + .5, kolvo)
	xt = plt.xticks(0)[0]
	plt.xticks(xt,[' '] * len(xt))

	remove_border(left=False, bottom=False)
	plt.grid(axis = 'x',color = 'white', linestyle = '-')

	plt.ylim(pos.max(), pos.min() - 1)
	plt.xlim(0,30)

# Функция главная
def main():

	path = 'vacancy_list.csv'  
	lvac = []
	page_count = 1

	url = get_vac()

	if page_count > get_page_count(get_html(url)):
		page_count = get_page_count(get_html(url))

	for page in range(0,page_count):
		print('Парсинг %d%%' % (page / page_count * 100))
		lvac.extend(parse(get_html(url.replace('page=0','page=%d' % page))))

	print('Парсинг %d%%' % (100))

	cld = datacl(lvac)
	pairs = fintr(cld)

	drimage(pairs)

	write_csv(pairs,path)

	#for i in cld:
	#	print(i)

	#print(len(lvac))

if __name__ == '__main__':
    main()

