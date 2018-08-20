#!/usr/bin/python
# -*- coding: utf-8 -*-
u'''
Mananciais São Paulo.
Mauro Zac | maurozac@gmail.com

Script auxiliar para gerar gráficos de N dias anteriores à data atual.

Feito em python 2
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
from preparar_os_dados import corrige, consolida
from rodar_analise import chuva_vs_var, eficiencia_corrente, prognostico
from atualizar_site import upload

PATH = "/home/ubuntu/mananciais/"
N = 100  # numero de dias para retroagir em relacao ao csv existente

def retroagir():
    u'''
    Abre os dados em mananciaisSerie.csv e executa as rotinas de construção
    dos gráficos e indicadores.
    '''
    f = open(PATH + 'data/mananciaisSerie.csv', 'r')
    serie = [x.split(';') for x in f.read().split('\r\n')][:-1]
    f.close()
    # exemplo serie[0] = ['2003-1-1', '52,9671', '0,0261']
    for n in range(N):
        chuva = [float(r[2].replace(',','.')) for r in serie]
        volume = [float(r[1].replace(',','.')) for r in serie]
        L = len(serie)
        dia = serie[-1][0].split('-')
        dia.reverse()
        HOJE = '.'.join(dia)
        chuva_vs_var(chuva, volume, L, HOJE)
        eficiencia_corrente(chuva, volume, L, HOJE)
        prognostico(chuva, volume, L, HOJE)
        serie.pop()

corrige()
consolida()
retroagir()
upload()
