#!/usr/bin/python
# -*- coding: utf-8 -*-
u'''
Mananciais São Paulo.
Mauro Zac | maurozac@gmail.com

Microservice 2: Corrigir e preparar os dados para a análise

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
import json

PATH = "/home/ubuntu/mananciais/"


def corrige():
    u'''
    Lê dados em mananciais.csv e corrige proporções, adiciona volume real e
    salva em manciais_corrigido.csv
    '''
    vCANT = 1269.6  # util + morto
    vCANTref = 982.07   # util
    vCANT_ad = 287.5   # adicioanal antes de 16/05/2014
    vALTO = 559.1
    vALTOref = 519.01 # util antigo
    vALTO_ad = 40   # adicional antes de 14/12
    vGUAR = 171
    vCOTI = 16
    vRIOG = 112
    vRIOC = 13
    f = open(PATH + 'mananciais.csv','r')
    dados = []
    for linha in f:
        campos = linha.split(';')
        # o modo de construir o indice vai mudando no tempo
        # Cantareira
        if campos[1] == 'sistemaCantareira':
            if campos[0] == '2014-5-16':
                vCANT_ad = 105.0 # adicioanal de 16/05/2014 a 23/10/2014
            if campos[0] == '2014-10-24': # adicioanal de 24/10/2014 a 2017-5-14
                vCANT_ad = 0
            if campos[0] == '2017-5-15': # nova ref a partir de 2017-5-15
                vCANT_ad = 287.5  # volta para a conta antiga
            volume = vCANT_ad + (vCANTref)*float(campos[2].split()[0].replace(',','.'))/100
            percent = str(round(100*volume/vCANT,1)).replace('.',',')+' %'
        # Alto Tiete
        elif campos[1] == 'sistemaAltoTiete':
            if campos[0] == '2014-12-14':
                vALTO_ad = 0
            volume = vALTO_ad + (vALTOref)*float(campos[2].split()[0].replace(',','.'))/100
            percent = str(round(100*volume/vALTO,1)).replace('.',',')+' %'
        # Guarapiranga
        elif campos[1] == 'sistemaGuarapiranga':
            volume = vGUAR*float(campos[2].split()[0].replace(',','.'))/100
            percent = campos[2]
        # Cotia
        elif campos[1] == 'sistemaCotia':
            volume = vCOTI*float(campos[2].split()[0].replace(',','.'))/100
            percent = campos[2]
        # Rio Grande
        elif campos[1] == 'sistemaRioGrande':
            volume = vRIOG*float(campos[2].split()[0].replace(',','.'))/100
            percent = campos[2]
        # Rio Claro
        elif campos[1] == 'sistemaRioClaro':
            volume = vRIOC*float(campos[2].split()[0].replace(',','.'))/100
            percent = campos[2]
        else:
            continue
        hm3 = str(round(volume, 1)).replace('.',',') + ' hm3'
        dados.append(';'.join([campos[0], campos[1], percent, hm3, campos[3], campos[4], campos[5]]))
    f.close()
    corrigido = open(PATH + 'data/mananciais_corrigido.csv', 'w')
    corrigido.writelines(dados)
    corrigido.close()


def consolida():
    u'''
    Lê dados de mananciais_corrigido.csv e consolida em uma lista de
    3-tuplas: (data, volume %, chuva mm)
    Salva em mananciaisSerie.csv => dados úteis
    ** chuva dos dias 29.fev são somados aos dias 28.fev e considera em 28 o
    volume de 29 para tornar o ciclo das séries homogêneos
    Cria e salva primeira versao de mananciais.json => para ajax do site
    '''
    # composicao relativa de cada reservatorio no estoque total de agua
    CANT = 0.593
    ALTO = 0.261
    GUAR = 0.08
    COTI = 0.007
    RIOG = 0.052
    RIOC = 0.006
    vTotal = 2140.7
    f = open(PATH + 'data/mananciais_corrigido.csv', 'r')
    dados = []
    for linha in f:
        campos = linha.split(';')
        if campos[1] == 'sistemaCantareira':
            volume = CANT * float(campos[2].split()[0].replace(',','.'))
            chuva = CANT * float(campos[4].split()[0].replace(',','.'))
        elif campos[1] == 'sistemaAltoTiete':
            volume += ALTO * float(campos[2].split()[0].replace(',','.'))
            chuva += ALTO * float(campos[4].split()[0].replace(',','.'))
        elif campos[1] == 'sistemaGuarapiranga':
            volume += GUAR * float(campos[2].split()[0].replace(',','.'))
            chuva += GUAR * float(campos[4].split()[0].replace(',','.'))
        elif campos[1] == 'sistemaCotia':
            volume += COTI * float(campos[2].split()[0].replace(',','.'))
            chuva += COTI * float(campos[4].split()[0].replace(',','.'))
        elif campos[1] == 'sistemaRioGrande':
            volume += RIOG * float(campos[2].split()[0].replace(',','.'))
            chuva += RIOG * float(campos[4].split()[0].replace(',','.'))
        elif campos[1] == 'sistemaRioClaro':
            volume += RIOC * float(campos[2].split()[0].replace(',','.'))
            chuva += RIOC * float(campos[4].split()[0].replace(',','.'))
            dados.append([campos[0], volume, chuva])
        else:
            continue
    f.close()
    # dados de 29.fev sao somados a 28.fev para homogenizar o ciclo das series
    homo = []
    for d in dados:
        if d[0][4:] == '-2-29':
            homo[-1][1] = d[1] # dia 28 assume volume do dia 29
            homo[-1][2] += d[2] # soma chuva de 29 em 28
        else:
            homo.append(d)
    # serie util
    serie = open(PATH + 'data/mananciaisSerie.csv', 'w')
    for item in homo:
        linha = ';'.join([item[0], str(item[1]).replace('.',','), str(item[2]).replace('.',',')])
        serie.write(linha + '\r\n')
    serie.close()
    # json resumo
    tend = 'manteve-se em'
    if round(homo[-1][1] - homo[-2][1],2) > 0: tend = 'subiu para'
    if round(homo[-1][1] - homo[-2][1],2) < 0: tend = 'caiu para'
    dia = homo[-1][0].split('-')
    dia.reverse()
    hoje = '.'.join(dia)
    dia_ = homo[-2][0].split('-')
    dia_.reverse()
    ontem = '.'.join(dia_)
    ajax = {
        'fonte': 'Probabit',
        'url': 'http://www.probabit.com.br/mananciais.html',
        'data': hoje,
        'ontem': ontem,
        'chuva': str(round(homo[-1][2],1)).replace('.',','),
        'estoque_hm3': str(int(round(homo[-1][1]*vTotal/100,0))),
        'estoque_p': str(homo[-1][1])[:5].replace('.',',')+'%',
        'estoque_24h_hm3': str(round((homo[-1][1]*vTotal/100 - homo[-2][1]*vTotal/100),1)).replace('.',','),
        'estoque_24h_p': str(round(homo[-1][1] - homo[-2][1],2)).replace('.',',')+'%',
        'sentido': tend,
        'chuva_mm_ano': str(int(round(sum([ch[2] for ch in homo[-365:]]),0))),
    }
    j = open(PATH + 'data/mananciais.json', 'w')
    j.write(json.dumps(ajax, indent=2))
    j.close()
