#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from bs4 import BeautifulSoup

url_base = 'http://v26.multidata.cl/warpit/json'

opt = {
    'rut' : 'apiowners/rut',
    'rut_extra' : 'apiowners/extra',
    'patente' : 'apicars/rels',
    'patente_extra' : 'apicars/extra',
    'patente2': 'apicars/plate'
}

def digito_verificador(rut):
    value = 11 - sum([ int(a)*int(b)  for a,b in zip(str(rut).zfill(8), '32765432')])%11
    return {10: 'K', 11: '0'}.get(value, str(value))

def peticion(que, dato):
    dato = dato.upper()
    URL = '%s/%s/%s/' % (url_base, que, dato)
    payload = {
        'device': '123123123123',
        'appcode': '2.6_android'
    }

    session = requests.session()
    r = requests.post(URL, data=payload, auth=('demo', 'demo'))
    datos = json.loads(r.text)
    #print(json.dumps(datos, indent=4))
    return datos

def ppeticion(rut):
    url2 = "http://buscardatos.com/cl/personas/padron_cedula_chile.php"
    payload2 = {
        'cedula': rut
    }
    r = requests.post(url2, data=payload2)
    soup = BeautifulSoup(r.text, 'html.parser')

    datos = {}

    last = ""
    for td in soup.find_all('td'):
        d = td.string
        d = d.strip().replace(":", "")
        if last == "sexo":
            datos['sexo'] = d

        if last == u"dirección":
            datos['direccion'] = d

        if last == u"circunscripción":
            datos['circunscripcion'] = d

        if last == "comuna":
            datos['comuna'] = d

        if last == "provincia":
            datos['provincia'] = d

        if last == u"región":
            datos['region'] = d

        if last == u"país":
            datos['pais'] = d
        last = d
    return datos


def tabular(data):
    for l in data:
        if len(l) > 1:
            print '%-12s%-5s%-32s' % (l[0], ':', l[1])
        else:
            lon = len(l[0])
            lon = int(round((50 - lon)/2))
            espacio = ' ' * lon
            titulo = espacio + l[0]
            print ''
            print titulo
            print '-'*50


def datosPatente(patentex):
    patente = peticion(opt['patente2'], patentex)
    persona = peticion(opt['patente'], patentex)

    if type(patente) is list:
        p = patente[0]
    else:
        p = patente

    pe = persona['0']
    rut = pe['Person']
    dv = digito_verificador(rut)

    rutraw = rut+dv
    rut2 = rut+'-'+dv

    pv = peticion(opt['rut_extra'], rutraw)
    px = ppeticion(rutraw)

    data = [
        [ "Datos del dueño" ],
        [ u'Dueño', pe['Name'] ],
        [ 'RUT', rut2 ],
        [ 'Nacionalidad', pv['chilena']['src'] ],
        [ 'Sexo', px['sexo'] ],
        [ u'País', px['pais'] ],
        [ u'Región', px['region'] ],
        [ u'Provincia', px['provincia'] ],
        [ 'Comuna', px['comuna'] ],
        [ u'Dirección', px['direccion'] ],
        [ "Datos del vehiculo" ],
        [ 'Patente', p['Plate'] ],
        [ 'Tipo', p['Class'] ],
        [ 'Marca', p['Maker'] ],
        [ 'Modelo', p['Model'] ],
        [ u'Año', p['Year'] ],
        [ 'Color', p['Color'] ],
        [ u'N° Motor', p['Motor'] ],
        [ 'Chasis', p['Chasis'] ]
    ]
    tabular(data)


datosPatente('fcbk24')
