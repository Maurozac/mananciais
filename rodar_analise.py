#!/usr/bin/python
# -*- coding: utf-8 -*-
u'''
Mananciais São Paulo.
Mauro Zac | maurozac@gmail.com

Microservice 3: Rodar a análise

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
import numpy as np
from scipy import stats
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
#http://stackoverflow.com/questions/2801882/generating-a-png-with-matplotlib-when-display-is-undefined?lq=1
mpl.use('Agg')
import matplotlib.pyplot as plt

PATH = "/home/ubuntu/mananciais/"

plt.style.use(PATH + 'mzac.mplstyle')


def chuva_vs_var(chuva, volume, L, HOJE):
    u'''Gera o grafico principal com os dados até HOJE e salva em formato png.

    Este gráfico unifica informações sobre o comportamento geral do sistema
    com milhares de pontos, a situação atual, a tendência e os níveis de risco.
    O eixo y foi escolhidos de modo a destacar a 2a derivada dos dados (ou seja,
    a variação da variação) permitindo assim a visualização linearizada do
    comportamento do sistema, o que facilita a compreensão visual e a tomada
    de decisão.

    Boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    -----------------------------------------------------------------------
    . alta densidade de informação
    . baixa densidade de elementos decorativos, redundantes ou dispensáveis
    . repetição do mesmo formato incentiva a comparação
    . incluir labels explicativos
    . o gráfico deve nos guiar em reflexões simples e complexas
    . visão geral e visões particulares sobrepostas e integradas
    . privilegiar relações lineares de causa e efeito
    . responder a perguntas pertinentes, esclarecer e apoiar a decisão
    ----------------------------------------------------------------------

    Paleta: https://encycolorpedia.com/

    #1f78b4 base: azul IG-USP #7ba3cd white shade
    #111111 branco
    #ff003f vermelho #ff7c7a white shade
    #000000 preto
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Mananciais de São Paulo',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylim=(-50, 50),
           ylabel=u'Variação do estoque em um ano (%)')
    # camada 1: areas indicativas de risco e atencao (branca, amarela, vermelha)
    ax.axhspan(-1 * volume[-1], -50, facecolor='#1f78b4', zorder=-1)
    ax.axhspan(0, -1 * volume[-1], facecolor='#7ba3cd', zorder=-1)
    ax.text(2195, max(-volume[-1], -48),u'– estoque:'+str(round(volume[-1], 1)).replace('.',',')+u'% –',
            family="monospace", fontsize='8', color='1',
            horizontalalignment='right', verticalalignment='center')
    # camada 2: dispersao xy com todos os pontos => contexto amplo e comportamento do sistema
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    ax.plot(x, y, marker='o', color='w')  # dispersao xy
    # camada 3: trajetoria recente => tendencia atual e situacao hoje
    ch0 = sum(chuva[-365:])
    ch30 = sum(chuva[-395:-30])
    ch60 = sum(chuva[-425:-60])
    ch90 = sum(chuva[-455:-90])
    ch120 = sum(chuva[-485:-120])
    vv0 = volume[-1] - volume[-1-365]
    vv30 = volume[-31] - volume[-31-365]
    vv60 = volume[-61] - volume[-61-365]
    vv90 = volume[-91] - volume[-91-365]
    vv120 = volume[-121] - volume[-121-365]
    ax.plot([ch0 , ch30, ch60, ch90], [vv0, vv30, vv60, vv90], color='#ff003f', ls='-', lw='3')
    ax.plot(ch0, vv0, marker='o', color='#ff003f', ls='', markersize=10)
    ax.plot(ch30, vv30, marker='o', color='#ff003f', ls='')
    ax.plot(ch60, vv60, marker='o', color='#ff003f', ls='')
    ax.plot(ch90, vv90, marker='o', color='#ff003f', ls='')
    ax.text(ch0+40, vv0-1, HOJE, family="monospace", fontsize='8',
            horizontalalignment='left', color='#ff003f',
            bbox={'facecolor':'1', 'pad':2, 'ec':'none', 'alpha':0.8})
    fig.savefig(PATH + 'data/graf' + str(L) + '.png')
    plt.close()


def regressao_1(chuva, volume, L, HOJE):
    u'''Gráfico que mede quanto o arranjo escolhido para a visualização é linear.
    Por construção, a reta ajustada corresponde à eficiência média do sistema,
    isto é, como ele em média se comporta frente a variações da oferta de água,
    ganha ou perde volume em que taxa?

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Curva de eficiência média',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylim=(-50, 50),
           ylabel=u'Variação do estoque em um ano (%)')
    # 1. pontos da dispersao xy
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    ax.plot(x, y, marker='o', color='#7ba3cd', ls='')
    # 2. curva (reta) de regressao
    # Para rodar a regressao o input precisa ser um array do Numpy
    # http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.linregress.html
    X = np.array(x)
    Y = np.array(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
    equi = -1 * (intercept) / slope
    line = slope * X + intercept
    ax.plot(X, line, color='1', ls='-')
    fig.text(0.6, 0.24, u'y = '+str(round(slope,3)).replace('.',',')+'.x '+str(round(intercept,3)).replace('.',','),
             family="monospace",fontsize='8',color='1')
             # bbox={'facecolor':'1', 'pad':4, 'ec':'none'})
    fig.text(0.6, 0.2, u'R2 = '+str(round(r_value**2,3)).replace('.',','),
             family="monospace",fontsize='8',color='1')
             # bbox={'facecolor':'1', 'pad':4, 'ec':'none'})
    fig.text(0.6, 0.16, u'Equilíbrio (y = 0): '+str(int(round(equi,0)))+ ' mm',
             family="monospace",fontsize='8',color='1')
             # bbox={'facecolor':'1', 'pad':4, 'ec':'none'})
    fig.savefig(PATH + 'data/regressao1.png')
    plt.close()


def regressao_2(chuva, volume, L, HOJE):
    u'''Gráfico que testa o efeito do aumento do volume do estoque.
    Este teste permite explorar uma propriedade importante do sistema, claramente
    evidenciada pelo modelo: o aumento do volume não muda a eficiência do sistema.
    O ponto de equilíbrio continua o mesmo, o que muda é a margem de segurança do
    armazenamento, o tamanho da banda para cima e para baixo. O sistema se torna
    capaz de lidar com maiores variações na oferta apenas por causa de seu tamanho,
    sem alterar sua eficiência.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    vAdicional = 988 # Billings - braço do Rio Grande
    vTotal = 2140.7
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Efeito Billings',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylim=(-50, 50),
           ylabel=u'Variação do estoque em um ano (%)')
    # 1. pontos da dispersao xy
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    y1 = [100*(volume[i]*vTotal/100 + vAdicional)/(vTotal+vAdicional) - 100*(volume[i-365]*vTotal/100 + vAdicional)/(vTotal+vAdicional) for i in range(365, L)]  # +Billings
    ax.plot(x, y1, marker='o', color='#7ba3cd', ls='')
    # 2. curvas (retas) de regressao
    X = np.array(x)
    Y = np.array(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
    equi = -1 * (intercept) / slope
    line = slope * X + intercept
    ax.plot(X, line, color='1', ls='-', lw='1')
    # com mais volume...
    Y1 = np.array(y1)
    slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(X, Y1)
    equi1 = - 1 * (intercept1) / slope1
    line1 = slope1 * X + intercept1
    ax.plot(X, line1, color='1', ls='-')
    fig.text(0.6, 0.24, u'y = '+str(round(slope1,3)).replace('.',',')+'.x '+str(round(intercept1,3)).replace('.',','),
             family="monospace",fontsize='8',color='1')
    fig.text(0.6, 0.2, u'R2 = '+str(round(r_value1**2,3)).replace('.',','),
             family="monospace",fontsize='8',color='1')
    fig.text(0.6, 0.16, u'Equilíbrio (y = 0): '+str(int(round(equi1,0)))+ ' mm',
             family="monospace",fontsize='8',color='1')
    fig.savefig(PATH + 'data/regressao2.png')
    plt.close()


def regressao_3(chuva, volume, L, HOJE):
    u'''Gráfico que testa o efeito do deslocamento do ponto de equilíbrio.
    Este teste mostra que um sistema mais eficiente, ou seja, que se equilibra
    com menor oferta de água também sofre os efeitos de acúmulo e perda em função
    da variação nas chuvas. A curva de eficiência se desloca para cima e permite
    visualizar que, na prática, o sistema apresenta variação na eficiência em
    diferentes momentos.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Armazenamento eficiente com chuvas a 1200 mm',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylim=(-50, 50),
           ylabel=u'Variação do estoque em um ano (%)')
    # 1. pontos da dispersao xy
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    ax.plot(x, y, marker='o', color='#7ba3cd', ls='')
    # 2. curvas (retas) de regressao
    X = np.array(x)
    Y = np.array(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
    equi = -1 * (intercept) / slope
    line = slope * X + intercept
    ax.plot(X, line, color='1', ls='-', lw='1')
    # com equilíbrio em 1200 mm
    b2 = -slope * 1200
    line2 = slope * X + b2
    ax.plot(X, line2, color='1', ls='-')
    fig.text(0.6, 0.24, u'y = '+str(round(slope,3)).replace('.',',')+'.x '+str(round(b2,3)).replace('.',','),
             family="monospace",fontsize='8',color='1')
    fig.text(0.6, 0.2, u'Equilíbrio (y = 0): 1200 mm',
             family="monospace",fontsize='8',color='1')
    fig.savefig(PATH + 'data/regressao3.png')
    plt.close()


def eficiencia_corrente(chuva, volume, L, HOJE):
    u'''Gráfico com a estimativa da eficiência corrente do sistema.
    Usa os dados dos últimos 120 dias da série.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Eficiência corrente (120 dias)',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylim=(-50, 50),
           ylabel=u'Variação do estoque em um ano (%)')
    # 1. pontos da dispersao xy
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    ax.plot(x, y, marker='o', color='#7ba3cd', ls='')
    ax.plot(x[-120:], y[-120:], marker='o', color='1', ls='')  # destacar
    # 2. curva (reta) de regressao, 120 dias
    X = np.array(x[-120:])
    Y = np.array(y[-120:])
    slopeA, interceptA, r_valueA, p_valueA, std_errA = stats.linregress(X,Y)
    # slopeA => coef. angular (+)
    # interceptA => coef. linear (-), so seria (+) se cruzasse y acima de 0
    equiA = -1 * interceptA / slopeA # x qdo y = 0
    lineE = slopeA * X + interceptA # todos os pontos x,y => a linha
    ax.plot(X, lineE, color='#ff003f', ls='-', lw='2')
    wH = sum(chuva[-365:])  # acumulado 1 ano hoje [+]
    ax.plot(equiA, 0, marker='o', color='#ff003f', ls='', markersize=10)  # chuva de equilibrio [verm]
    fig.text(0.6, 0.24, u'y = '+str(round(slopeA,3)).replace('.',',')+'.x '+str(round(interceptA,3)).replace('.',','),
             family="monospace", fontsize='8', color='1')
    fig.text(0.6, 0.2, u'R2 = '+str(round(r_valueA**2,3)).replace('.',','),
             family="monospace", fontsize='8', color='1')
    fig.text(0.6, 0.16, u'Equilíbrio (y = 0): '+str(int(round(equiA,0)))+ ' mm',
             family="monospace", fontsize='8', color='1')
    if wH <= equiA:
        ax.plot(wH, 0 , marker='v', color='#ff7c7a', ls='', markersize=10)  # chuva hoje [azul]
        ax.text(wH-20, 0,
                 u'Desvio:'+str(int(round(100*(equiA-wH)/(equiA), 0)))+'%',
                 family="monospace",fontsize='10',color='1',
                 horizontalalignment='right', verticalalignment='center')
    else:
        ax.plot(wH, 0 , marker='^', color='#ff7c7a', ls='', markersize=10)  # chuva hoje [azul]
        ax.text(wH+20, 0,
                 u'Desvio:'+str(int(round(100*(wH-equiA)/(equiA), 0)))+'%',
                 family="monospace",fontsize='10',color='1',
                 horizontalalignment='left', vertilalignment='center')
    fig.savefig(PATH + 'data/ef' + str(L) + '.png')
    plt.close()


def prognostico(chuva, volume, L, HOJE):
    u'''
    Este gráfico apresenta uma estimativa do tempo de duração do estoque de água
    caso a tendência corrente seja de queda. A estimativa é extendida em uma curva
    em função da chuva.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(title=u'Mananciais SP - Prognóstico',
           xlim=(800, 2200),
           xlabel=u'Acumulado de chuva em um ano (mm)',
           ylabel=u'Dias de estoque')
    # 1. usar eficiencia corrente: 120 dias
    x = [sum(chuva[i-365+1:i+1]) for i in range(365, L)]  # var chuva
    y = [volume[i] - volume[i-365] for i in range(365, L)]  # var volume
    X = np.array(x[-120:])
    Y = np.array(y[-120:])
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
    # 2. dias restantes de agua
    # sobre comportamento do modelo: o prognostico de acabar so faz sentido se a tendencia for de queda
    # qdo a conta para calcular zH fica com denominador zero -> tempo tende ao infinito
    # qdo denominador positivo -> tempo fica negativo: esta enchendo e nao esvaziando [inverte sinal]
    wH = sum(chuva[-365:]) # acumulado 1 ano hoje [+]
    zH = 4 * 365  # qualquer numero grande
    if slope * wH + intercept < 0: # ok, tendencia eh de queda
        zH = -365 * volume[-1] / (slope * wH + intercept) # zH: dias restantes
    # eixo y ajustavel => foco
    y_sup = int(zH + 100)
    ax.set_ylim((0, y_sup))
    # 3. curva de prognostico em funcao da chuva
    W = np.arange(810, 2191) # pode ocupar quase todo o range do eixo x
    z = [-365 * volume[-1] / (slope * w + intercept) for w in W]
    z = [i for i in z if i < y_sup and i > 0]  # para que fique dentro do grafico
    Z = np.array(z)
    if slope * wH + intercept < 0:
        # linha de referencia para a media historica
        y = np.arange(0, y_sup)
        x = [1441 for i in y]
        ax.plot(x, y, ls="--", lw='1', color='1')
        # curva
        ax.plot(W[:len(Z)], Z, color='1', ls='-')
        # ponto do best guess
        ax.plot(wH, zH, marker='o', color='#ff003f', ls='', markersize=10)
        ax.text(wH+30, zH, HOJE + u" duração do estoque:" + str(int(round(zH, 0))) + " dias",
                family="monospace", horizontalalignment='left', verticalalignment='center', color='1', fontsize='10')
    else:
        fig.text(0.5, 0.5, u"A tendência atual é de aumento no estoque",
                 family="monospace", horizontalalignment='center', color='1', fontsize='10')
    fig.savefig(PATH + 'data/prog' + str(L) + '.png')
    plt.close()


def sazonalidade(serie, HOJE):
    u'''
    Este gráfico mostra a oscilação sazonal do estoque. A curva principal é obtida
    pela média de volume de todos os anos, as curvas secundárias são as bandas de variação
    em quartis.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    # 0. eixos e escalas
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    ax.set(
        xlabel=u'Dias do ano',
        xlim=(1, 365),
        xticks=np.arange(0, 365, 30),
        ylabel=u'Água em estoque (%)',
        ylim=(0, 100))
    # preparacao dos dados a partir da serie bruta
    anos = {}
    for i in range(0, len(serie), 365):
        anual = serie[i:i+365]
        anos[anual[0][0][:4]] = {
            'volume': [float(d[1].replace(',','.')) for d in anual],
        }
    ax.set_title(u'Média do volume 2003 a ' + unicode(2003 + len(anos) - 1))
    vol_medio = []
    for i in range(365):
        volume = []
        for j in range(0, len(anos)):
            try:    # pq ultimo ano é incompleto
                volume.append(anos[str(2003+j)]['volume'][i])
            except:
                pass
        # listas com (media, min, q-inf, mediana, q-sup, max)
        v = np.array(volume)
        vol_medio.append((np.mean(v), np.min(v), np.percentile(v,25), np.median(v), np.percentile(v,75), np.max(v)))
    ax.plot([v[0] for v in vol_medio], c='1', ls='-')
    ax.plot([v[1] for v in vol_medio], c='1', ls='--', lw=1)
    ax.plot([v[2] for v in vol_medio], c='1', ls='--', lw=1)
    ax.plot([v[3] for v in vol_medio], c='1', ls='-', lw=1)
    ax.plot([v[4] for v in vol_medio], c='1', ls='--', lw=1)
    ax.plot([v[5] for v in vol_medio], c='1', ls='--', lw=1)
    ax.text(369, vol_medio[-1][5], u'máximo', color='0', fontsize='8')
    ax.text(369, vol_medio[-1][4], u'+25%', color='0', fontsize='8')
    ax.text(369, vol_medio[-1][3], u'mediana', color='0', fontsize='8')
    ax.text(369, vol_medio[-1][2], u'-25%', color='0', fontsize='8')
    ax.text(369, vol_medio[-1][1], u'mínimo', color='0', fontsize='8')
    volume_hoje = float(serie[-1][1].replace(',','.'))
    ax.plot(len(anual), volume_hoje, marker='o', color='#ff003f', ls='', markersize=10)
    ax.text(len(anual)-3, volume_hoje-5, HOJE, family="monospace", fontsize='10',
            horizontalalignment='left', verticalalignment='center', color='1')
    fig.savefig(PATH + 'data/oscila.png')
    plt.close()


def estoque_anos(serie, HOJE):
    u'''
    Coleção de gráficos da série histórica do volume em estoque e da chuva.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    anos = {}
    for i in range(0, len(serie), 365):
        anual = serie[i:i+365]
        anos[anual[0][0][:4]] = {
            'volume': [float(d[1].replace(',','.')) for d in anual],
            'chuva': [float(d[2].replace(',','.')) for d in anual],
        }
    for k, i in anos.items():
        ax.set(title=k,
            xlabel=u'Dias do ano',
            xlim=(1, 365),
            xticks=np.arange(0, 365, 30),
            ylabel=u'Água em estoque (%)',
            ylim=(0, 100))    # preparar dados a partir da serie bruta
        ax.text(10, 5, 'chuva (mm)', color='0', fontsize=8, bbox={'facecolor':'1', 'pad':4, 'ec':None})
        volume = i['volume']
        chuva = i['chuva']
        ax.plot(volume, c='1', ls='-')
        ax.plot(chuva, c='1', ls='-', lw=0.5)
        fig.savefig(PATH + 'data/estoque' + k + '.png')
        ax.clear()
    plt.close()


def padroes_anos(serie, HOJE):
    u'''
    Coleção de gráficos com todos os pontos da disperção xy destacando os pontos
    adicionados em cada ano. O padrão de sobreposição dos pontos permite inferir
    o caminho percorrido no tempo.

    Contém: boas práticas de visualização de dados (inspirado em E. Tufte e S. Few)
    '''
    fig, ax = plt.subplots()
    fig.text(0.9, 0.91, u'Probabit '+ HOJE, family="monospace", fontsize='6', color='#1f78b4', horizontalalignment='right')
    # prepara dados e cria grafico para cada ano
    anos = [a for a in range(2003, int(HOJE[-4:])+1)]
    for ANO in anos:
        ax.set(title=str(ANO) + '/' + str(ANO-1),
            xlabel=u'Acumulado de chuva em um ano (mm)',
            xlim=(800, 2200),
            ylabel=u'Variação do estoque em um ano (%)',
            ylim=(-50, 50))    # preparar dados a partir da serie bruta
        x, y, x2, y2 = [], [], [], []
        for i in range(365, len(serie)):
            if int(serie[i][0][:4]) != ANO:
                y.append(float(serie[i][1].replace(',','.')) - float(serie[i-365][1].replace(',','.')))
                x.append(sum([float(c[2].replace(',','.')) for c in serie[i-365+1:i+1]]))
            else:
                y2.append(float(serie[i][1].replace(',','.')) - float(serie[i-365][1].replace(',','.')))
                x2.append(sum([float(c[2].replace(',','.')) for c in serie[i-365+1:i+1]]))
        ax.plot(x, y, marker='o', color='#7ba3cd', ls='')
        ax.plot(x2, y2, marker='o', color='1', ls='')
        fig.savefig(PATH + 'data/chuva_vs_vol' + str(ANO) + '.png')
        ax.clear()
    plt.close()


def modelo():
    u'''
    Abre os dados em mananciaisSerie.csv e executa as rotinas de construção
    dos gráficos e indicadores.
    '''
    f = open(PATH + 'data/mananciaisSerie.csv', 'r')
    serie = [x.split(';') for x in f.read().split('\r\n')][:-1]
    f.close()
    # exemplo serie[0] = ['2003-1-1', '52,9671', '0,0261']
    chuva = [float(r[2].replace(',','.')) for r in serie]
    volume = [float(r[1].replace(',','.')) for r in serie]
    L = len(serie)
    dia = serie[-1][0].split('-')
    dia.reverse()
    HOJE = '.'.join(dia)
    chuva_vs_var(chuva, volume, L, HOJE)
    regressao_1(chuva, volume, L, HOJE)
    regressao_2(chuva, volume, L, HOJE)
    regressao_3(chuva, volume, L, HOJE)
    eficiencia_corrente(chuva, volume, L, HOJE)
    prognostico(chuva, volume, L, HOJE)
    sazonalidade(serie, HOJE)
    estoque_anos(serie, HOJE)
    padroes_anos(serie, HOJE)
