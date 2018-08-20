#!/usr/bin/python
# -*- coding: utf-8 -*-
u'''
Mananciais São Paulo.
Mauro Zac | maurozac@gmail.com

Microservice 4: Atualizar material para site estático servido na S3

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
import boto
import shutil
import os

AWS_ID = 'seu_id'
AWS_KEY = 'sua_key'
PATH = "/home/ubuntu/mananciais/"


def upload():
    u"""
    Conecta e sobe novos arquivos para a S3.
    Apaga tudo do local, exceto html e série de referência
    """
    # serie original precisa ter copia mantida no root do path
    shutil.copy(PATH+'mananciais.csv', PATH+'data/mananciais.csv')
    s3 = boto.connect_s3(aws_access_key_id=AWS_ID, aws_secret_access_key=AWS_KEY)
    bucket = s3.lookup('www.probabit.com.br')
    for root, dirs, files in os.walk(PATH + 'data'):
        for f in files:
            if f is not '.DS_Store':
                key = bucket.new_key(os.path.join('mananciais', f))
                key.set_contents_from_filename(os.path.join(root, f), policy='public-read')
                # limpa dados do disco local
                os.remove(os.path.join(root, f))
    # html
    key = bucket.new_key('mananciais.html')
    key.set_contents_from_filename(PATH + 'mananciais.html', policy='public-read')
