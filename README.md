# Mananciais de São Paulo
Um exercício de ciência de dados e micro arquitetura.

http://www.probabit.com.br/mananciais.html

O site é um html estático servido diretamente da S3. Os scripts rodam em uma instância ubuntu da AWS, ativados diariamente via crontab:

```
39 12 * * * /usr/bin/python /home/ubuntu/mananciais/mananciais.py >/dev/null 
```
