#!/usr/bin/python3

# Este script servirá para meter um url do youtube ou um termo de procura, e a
# partir daí fazer play da próxima canção sugerida.

# Versão 5.1
# - Correcção para quando não existe input.

# Mais alterações a fazer:
# - Aceitar playlists (listas de videos)
# - Lidar com maus inputs e fazer print do modo de utilização

import urllib.request as ur
from sys import argv
from os import system
from subprocess import Popen, PIPE
from math import ceil




def code2url(code_in):
    return "https://www.youtube.com/watch?v=" + code_in




def code2url_img(code_in):
    return "https://i.ytimg.com/vi/"+ code_in + "/hqdefault.jpg"




def search_txt_to_code(list_in):
    # Procura do código correspondente aos termos de procura
    
    str_search = ''
    for s in list_in[:-1]:
        str_search += s + '+'
    str_search += list_in[-1]
    url0 = 'https://www.youtube.com/results?search_query='
    url1 = '=&utm_source=opensearch'
    url_search = url0 + str_search + url1

    #print("[radio_yt]", url_search)
    page = ur.urlopen(url_search)
    txt = page.read().decode()

    i0 = txt.find('yt-thumb-simple')
    i1 = txt.find('video-ids=\"',i0)+11

    code = txt[i1:i1+11]

    return code




def parse_input(list_in):
    # Dado o input do terminal, quero obter o codigo do video
    
    # Verificar se não foi introduzido input
    if len(list_in) == 1:
        print("Usage:")
        print(list_in[0], "search_terms | youtube_url")
        exit(1)
    else:
        list_search = list_in[1:]
    
    # Flag para apenas fazer play uma vez
    f_single = 0
    
    if list_search[0] == '-1':
        f_single = 1
        list_search = list_in[2:]

    if list_search[0][0:32] == 'https://www.youtube.com/watch?v=':
        # Caso seja um url
        code = list_search[0][32:]
    else:
        # Procura do video
        code = search_txt_to_code(list_search)

    return [code, f_single]




def parse_html_chars(txt):
    parse_list = {
    "&quot;" : "\"",
    "&amp;"  : "&",
    }
    
    i = 0
    txt_out = ""
    for k in range(len(txt)):
        if txt[k] != '&':
            continue

        txt_out += txt[i:k]
        i = txt.find(';', k) + 1
        char_html = txt[k:i]

        # Caso o caracter seja um código numérico
        if char_html[1] == "#":
            txt_out += chr( int(char_html[2:-1]) )
            continue

        # Caso o caracter não esteja na lista, simplesmente adiciona o que
        # está no html.
        if char_html in parse_list:
            txt_out += parse_list[char_html]
        else:
            print("Falta o caracter:", char_html)
            txt_out += char_html

    txt_out += txt[i:]
    return txt_out




def print_cool_title(title):

    tam = len(title)

    out,err = Popen(["stty","size"], stdout=PIPE).communicate()
    raw = out.decode().split()
    medidas = [int(x) for x in raw]
    H = medidas[0]
    W = medidas[1]
    w_box = min(W, tam+4)
    w_txt = w_box - 4
    n_linhas = int(ceil(tam/w_txt))
    
    #padding
    title += " "*( n_linhas*w_txt - tam )

    print()
    print("#"*w_box)
    # Print do corpo
    for k in range(n_linhas):
        print("# " + title[k*w_txt:(k+1)*w_txt] + " #")
    print("#"*w_box)
    print()




# next_vid()
# Encontra uma sugestão que ainda não tinha sido reproduzida.
# Estou a assumir que a lista de videos sugeridos é suficientemente grande para
# encontrar um vídeo ainda não reproduzido.
def next_vid(txt):
    global played_vids
    
    i0 = 0
    i1 = 0
    while True:
        i0 = txt.index("content-wrapper", i1)
        i1 = txt.index("?",i0)
        code = txt[i1+3:i1+14]
        if code not in played_vids:
            break

    return code




# play_vid()
# Play do video correspondente ao code.
# Retorna o code do próximo vídeo
def play_vid(code):
    
    # Actualização da lista de videos já reproduzidos.
    global played_vids
    played_vids += [code]

    url = code2url(code)
    img = code2url_img(code)
    
    page = ur.urlopen(url)
    txt = page.read().decode()

    # Procura do título
    i0 = txt.index("<title>") + 7
    i1 = txt.index("</title>") - 10
    title = txt[i0:i1]
    # Acerto dos caracteres especiais
    title = parse_html_chars(title)
    # Formatação especial para ser usado em comandos externos
    title_cmd = title.replace("\"", "\\\"")
    
    print_cool_title(title)
    
    system("wget -q " + img + " -O /tmp/hqdefault.jpg")
    system("notify-send -i /tmp/hqdefault.jpg " + '"'  + title_cmd + '"')
    mpv_opt = "--no-video --cache=1024 --ytdl-raw-options=limit-rate=1024K"
    exit_status = system( "mpv %s %s"%(mpv_opt, url) )
    
    # Caso o mpv seja interrompido com o ctrl+c, significa que quero parar com o
    # stream.
    if exit_status == 2:
        print("[radio_yt] Goodbye\n")
        exit(1)

    # Separação para o próximo vídeo
    print("\n\n")

    # Próximo video
    code = next_vid(txt)

    return code 




################################################################################
################################################################################

# Lista dos videos já reproduzidos
global played_vids
played_vids = []

# Parsing do input
code, flag_single = parse_input(argv)

if flag_single:
    play_vid(code)
    exit(0)

while 1:
    code = play_vid(code)
