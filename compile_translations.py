# This script is for finding translatable strings within React app that are missing translations

import re
import os
import json

i18nPath = 'i18n/'
searchPaths = [
    # 'packages/',
    # 'src/'
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
                    result += content[i] +  content[i + 1]
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
                    if match.decode('utf-8') not in translationMap:
                        totalMatches.append(match)

    return totalMatches

for match in scan():
    print(match)