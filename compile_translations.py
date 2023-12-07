# This script is for finding translatable strings within React app that are missing translations

import re
import os
import json
import csv

i18nPath = '../scandipwa/i18n/'
searchPaths = [
    '../scandipwa/src/',
    '../scandipwa/packages/',
]

totalMatches = []

def extractTranslatableStrings(content):
    i = 0
    matches = []

    while i < len(content) - 2:
        lookAhead = content[i] + content[i + 1] + content[i + 2]

        if lookAhead == '__(':
            result = ""

            while content[i] not in '\'`"':
                i += 1

                if i >= len(content):
                    return matches

            quote = content[i]
            i += 1

            while content[i] != quote:
                result += content[i]
                i += 1

                if content[i] == '\\' and content[i + 1] == quote:
                    result += content[i + 1]
                    i += 2

                if i >= len(content):
                    return matches

            matches.append(result)

        i += 1

    return matches

def compileTranslationMap():
    translationMap = []

    for subdir, dirs, files in os.walk(i18nPath):
        for fileName in files:
            if ".json" not in fileName:
                continue

            path = os.path.join(subdir, fileName)
            file = open(path)
            data = json.load(file)

            for key in data:
                value = data[key]

                if not value or key == value:
                    continue

                if key not in translationMap:
                    translationMap.append(key)

    return translationMap

def scan():
    totalMatches = []
    translationMap = compileTranslationMap()

    for searchPath in searchPaths:
        for subdir, dirs, files in os.walk(searchPath):
            for fileName in files:
                path = os.path.join(subdir, fileName)
                file = open(path)
                fileContent = file.read()

                for match in extractTranslatableStrings(fileContent):
                    if match not in translationMap:
                        totalMatches.append(match)

    return totalMatches

# for match in scan():
    # print(match)

def compileFullTranslationMap():
    translationMap = {}

    for subdir, dirs, files in os.walk(i18nPath):
        for fileName in files:
            if ".json" not in fileName:
                continue

            path = os.path.join(subdir, fileName)
            file = open(path)
            data = json.load(file)
            lang = fileName.replace('.json', '')
            translationMap[lang] = {}

            for key in data:
                value = data[key]

                if not value or key == value:
                    continue

                if key not in translationMap[lang]:
                    translationMap[lang][key] = value.encode('utf-8')

    return translationMap


def getExists(translationMap, value):
    exists = {}

    for key in translationMap:
        map = translationMap[key]

        if value not in map:
            exists[key] = False
        else:
            exists[key] = True

    return exists

def scanSmarter(translationMap):
    exists = {}

    for searchPath in searchPaths:
        for subdir, dirs, files in os.walk(searchPath):
            for fileName in files:
                path = os.path.join(subdir, fileName)
                file = open(path)
                fileContent = file.read()
                strings = extractTranslatableStrings(fileContent)

                if len(strings):
                    for match in strings:
                        if match not in exists:
                            total = True
                            val = getExists(translationMap, match)

                            for k in val:
                                v = val[k]
                                total = total and v

                            if not total:
                                exists[match] = [val, path]

    return exists

translationMap = compileFullTranslationMap()
exists = scanSmarter(translationMap)

with open('translations.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(['en_GB'] + translationMap.keys() + ['location'])

    for k in exists:
        v = exists[k]
        out = [k]

        for lang in v[0]:
            if k in translationMap[lang]:
                out.append(translationMap[lang][k])
            else:
                out.append('MISSING')

        out.append(v[1].replace('../scandipwa/', ''))

        writer.writerow(out)
