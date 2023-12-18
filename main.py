import nltk  # библиотека для обработки естественного языка
import pymorphy3
import wikipedia
from fuzzywuzzy import fuzz
from nltk.tokenize import word_tokenize
import requests
from requests.exceptions import ConnectTimeout


nltk.download('punkt')
morph = pymorphy3.MorphAnalyzer(lang='ru')
amount = 100

# метод Джаро-Винклера
def correct_spelling(input_str, options):
    best_match = max(options, key=lambda option: fuzz.token_set_ratio(input_str, option))
    print(best_match)
    return best_match

# удаляем знаки препинания
def delete_punctuation_marks(text):
    punc = "!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~»«—–-1234567890"
    return "".join([ch if ch not in punc else '' for ch in text])

# лемматизируем слово
def normalization(text):
    return "".join([morph.parse(w)[0].normal_form for w in word_tokenize(text)])

# токенезируем текст
def data_processing(text): 
    return delete_punctuation_marks(normalization(text.strip()))

# сохраняем токенизированный текст в файл
def lemmatization(text, number):
    array_of_tokens = word_tokenize(text, language='russian')
    with open(f'tokens/{number}.txt', 'w', encoding='utf-8') as file:
        for token in array_of_tokens:
            token = data_processing(token)
            file.write(token + '\n')
        file.close()

# обработка рекурсии и таймаута при запросе
def find_only_one(page, num):
    obj = ''
    try:
        obj = wikipedia.page(page)
        print(obj)
    except wikipedia.exceptions.HTTPTimeoutError as e:
        if(num < 10):
            obj = find_only_one(page, num + 1)
    except ConnectTimeout as e:
        if(num < 10):
            obj = find_only_one(page, num + 1)
    except wikipedia.DisambiguationError as e:
        if(num < 10):  
            try:
                obj = find_only_one(e.options[num], num + 1)
            except IndexError:
                print('Не повезло')
    return obj

# поиск страниц
def search_wikipedia(amount):
    theme = input('Категория: ')
    print(" ")
    wikipedia.set_lang('ru')
    ind = 1
    pages = wikipedia.search(theme, amount)
    print("Найденные тексты:")
    for i in range(1,len(pages) + 1):
        print(str(i) + ': ' + pages[i])

    for page in pages:
        wiki_page = find_only_one(page, 0)
        with open(f'pages_wiki/{ind}.txt', 'w', encoding='utf-8') as file:
            try:
                file.write(wiki_page.original_title + '\n' + wiki_page.summary)
                lemmatization(wiki_page.original_title + ' ' + wiki_page.summary, ind)
                with open('index.txt', 'a+', encoding='utf-8') as index:
                    index.write(str(ind) + ' ' + wiki_page.url + '\n')
                    index.close()
            except:
                lemmatization('', ind)
                file.write('Ошибка при загрузке страницы')
            file.close()
            
        ind += 1


# search_wikipedia(amount)
dict_url = dict() # словарь формата 'индекс: ссылкка'

with open('index.txt', 'r', encoding='utf-8') as index:
    for line in index:
        line = line.split(' ')
        dict_url[line[0]] = line[1][:-1]

unrepeated_set = set()  # набор слов для упрощеняи процесса индексации
inverted_index = dict() # структура инвертированного индекса

for i in range(1, amount):
    with open(f'tokens/{i}.txt', 'r', encoding='utf-8') as tokens:
        for word in tokens:
            word = word[:-1]
            if word in unrepeated_set:
                if i not in inverted_index.get(word):
                    inverted_index.get(word).append(i)
                    continue
                continue
            inverted_index[word] = [i]
            unrepeated_set.add(word)
print(" ")

query = input('Запрос: ').lower()
query = correct_spelling(query, list(inverted_index.keys()))
print('Найденные по запросу страницы:')

try:
    for url in inverted_index.get(query):
        print('  Ссылка: ' + dict_url.get(f'{url}'))
except:
    print('По вашему запросу ничего не найдено. \n')

# print(inverted_index)