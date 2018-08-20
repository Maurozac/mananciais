#!/usr/bin/python
# -*- coding: utf-8 -*-
u'''
Mananciais São Paulo.
Mauro Zac | maurozac@gmail.com

Microservice 1: Pegar dados na Sabesp

--------------------------------------------------------------------------------
Copyright 2015 Mauro Zackiewicz (under the New BSD License)

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------------
'''
import datetime
import time
import requests  # instalar http://docs.python-requests.org/pt_BR/latest/

# local onde roda o script
PATH = "/home/ubuntu/mananciais/"

def scrapper_sabesp(dia, mes, ano):
    u'''
    É preciso pescar os dados de dentro do html da Sabesp
    A estrutura pode mudar sem aviso prévio => corrigir aqui as regras
    entra: str, str, str
    retorna: None or 6-tupla com dados de interesse
    '''
    url = 'http://www2.sabesp.com.br/mananciais/DivulgacaoSiteSabesp.aspx'
    r1 = requests.get(url)
    # hackeando ...
    viewstate = r1.text.split('id="__VIEWSTATE" value="')[1].split('" />')[0]
    valid = r1.text.split('id="__EVENTVALIDATION" value="')[1].split('" />')[0]
    data = {'__VIEWSTATE': viewstate,
            '__EVENTVALIDATION': valid,
            '__VIEWSTATEENCRYPTED': '',
            'cmbDia': dia,
            'cmbMes': mes,
            'cmbAno': ano,
            'Imagebutton1.x': 11, 'Imagebutton1.y': 13,
            }
    try:
        time.sleep(5)
        r2 = requests.post(url, data=data)
    except:
        return None
    # d1 = r2.text.split(u'volume armazenado</td><td class="guardaImgBgDetalhe" width="88">')
    # nova versao: maio 2017
    d1 = r2.text.split(u'ndice armazenado</td><td class="guardaImgBgDetalhe" width="68">')
    volume = []
    for i in d1:
        if i[1:10] == "ndice 1: ":  # novo formato sabesp, desde 20/jun/2015
            volume.append(i[10:17].split()[0] + ' %')
        else:
            volume.append(i[:7].split()[0] + ' %')
        # maio 2017: back
        # volume.append(i[:7].split()[0] + ' %')
    volume.pop(0)
    if len(volume) != 6:
        return None
    # d2 = r2.text.split(u'pluviometria do dia</td><td class="guardaImgBgDetalhe" width="88">')
    d2 = r2.text.split(u'pluviometria do dia</td><td class="guardaImgBgDetalhe" width="68">')
    chuva = []
    for i in d2:
        chuva.append(i[:8].split()[0] + ' mm')
    chuva.pop(0)
    if len(chuva) != 6:
        return None
    # d3 = r2.text.split(u'pluviometria acumulada no mês</td><td class="guardaImgBgDetalhe" width="88">')
    d3 = r2.text.split(u'pluviometria acumulada no mês</td><td class="guardaImgBgDetalhe" width="68">')
    acumulada = []
    for i in d3:
        acumulada.append(i[:8].split()[0] + ' mm')
    acumulada.pop(0)
    if len(acumulada) != 6:
        return None
    # d4 = r2.text.split(u'média histórica do mês</td><td class="guardaImgBgDetalhe" width="88">')
    d4 = r2.text.split(u'média histórica do mês</td><td class="guardaImgBgDetalhe" width="68">')
    media = []
    for i in d4:
        media.append(i[:8].split()[0] + ' mm')
    media.pop(0)
    if len(media) != 6:
        return None
    return (
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaCantareira', volume[0], chuva[0], acumulada[0], media[0]]),
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaAltoTiete', volume[1], chuva[1], acumulada[1], media[1]]),
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaGuarapiranga', volume[2], chuva[2], acumulada[2], media[2]]),
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaCotia', volume[3], chuva[3], acumulada[3], media[3]]),
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaRioGrande', volume[4], chuva[4], acumulada[4], media[4]]),
        ';'.join([ano+'-'+mes+'-'+dia, 'sistemaRioClaro', volume[5], chuva[5], acumulada[5], media[5]]),
        )


def webbot_sabesp(dt):
    '''
    1. abre mananciais.csv e verifica ultimo dia
    2. constroi casos para baixar, se for o caso
    3. executa scrapper_sabesp
    4. append em mananciais.csv

    entra: datetime
    sai: mananciais.csv no disco [microservice pattern]
    '''
    # 1
    arquivo = open(PATH + 'mananciais.csv', 'r')
    itens = [r for r in arquivo]
    arquivo.close()
    data = itens[-1].split(';')[0]
    if not data == str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day):
        # 2
        refs = [(str(dt.day), str(dt.month), str(dt.year))]  # hoje
        go = True
        while go:
            dt = dt - datetime.timedelta(1)
            if data == str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day):
                go = False
            else:
                refs.append((str(dt.day), str(dt.month), str(dt.year)))
        refs.reverse()
        # 3
        novos = [scrapper_sabesp(d[0], d[1], d[2]) for d in refs]
        tentativas = 1
        while None in novos:
            time.sleep(5)
            novos = [scrapper_sabesp(d[0], d[1], d[2]) for d in refs]
            tentativas += 1
            if tentativas > 10:
                break
        # 4
        arquivo = open(PATH + 'mananciais.csv', 'a')
        for n in novos:
            for s in n:
                arquivo.write(s + '\r\n')
        arquivo.close()
