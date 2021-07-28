# @Author: AshishKingdom(Ashish Kushwaha)

#help files parser related functions
import requests

def getRawDataFromQB64Wiki(keyword):
    #return the raw wiki data from http://qb64.org/wiki if it succeed
    #otherwise, we will be using data from the stored help files
    r = requests.get("http://qb64.org/wiki/index.php?action=edit&title="+keyword.upper())
    if(r.status_code==200):
        data = r.text
        return data[data.find('name="wpTextbox1">')+18:data.find("</textarea>")]
    else:
        f = open('help/'+keyword.upper()+'.txt', 'r')
        data = f.read()
        f.close()
        return data


def removeHTMLSpecialChars(s):
    d = {"&amp;":'&', "&lt;":'<', "&gt;":'>', "&nbsp;":' '}
    s2 = s
    for k in d.keys():
        s2 = s2.replace(k, d[k])
    return s2

def reformatStr(s, put_backtick=False): #coverts {{ABC|XYZ}} or [[ABC|XYZ]] to XYZ
    s2 = ""
    i = 0
    while(i<len(s)):
        c = s[i]
        if(s[i:i+2]=="{{" or s[i:i+2]=="[["):
            f1 = s.find('|', i+2)
            f2 = s.find('|', f1+1)

            if s[i:i+2]=="{{":
                end_sep = "}}"
            else:
                end_sep = "]]"
            end_pos = s.find(end_sep, i+2)

            if(f1>0):
                if(f2>f1):
                    if(f2<end_pos): 
                        f = f2
                    else:
                        if(f1>end_pos):
                            f = -1
                        else:
                            f = f1
                else:
                    if(f1>end_pos):
                        f = -1
                    else:
                        f = f1
            else:
                f = -1


            if(f==-1):
                c = s[i+2:s.find(end_sep, i+2)]
                #print(c)
                i = s.find(end_sep, i+2)+2
                if(put_backtick): c = '`'+c+'`'
            else:
                c = s[f+1:s.find(end_sep, f)]
                i = s.find(end_sep, f)+2
                #print(c, s, i)
                #input()
        else:
            i += 1
        s2 += c
    return s2

def replaceStr(s, f, r): #replaces every occurance of f with r in s
    s2 = s.replace(f, r)
    return s2


def getDocumentation(keyword):

    data = {"bytes":0, "title":keyword.upper(), "use":"", "{{PageSyntax}}":"", "{{PageParameters}}":"", "{{PageDescription}}":"", "{{PageAvailability}}":""}

    file_content = getRawDataFromQB64Wiki(keyword).split('\n')
    topics = ["{{PageSyntax}}", "{{PageParameters}}", "{{PageDescription}}", "{{PageAvailability}}"]
    current_topic = ""
    #parse the contents
    done_use = False
    i = 0
    while i<len(file_content):

        if(done_use==False):
            if(file_content[0][:15]=="{{DISPLAYTITLE:"):
                j = 1
            else:
                j = 0
            while(file_content[j].strip() not in topics):
                data["use"] += removeHTMLSpecialChars(file_content[j]).replace("'''",'').replace("''",'')+' '
                j += 1
            done_use = True
            current_topic = file_content[j].strip()
            i = j+1

        fc = file_content[i].strip()

        if(fc=="{{PageExamples}}" or fc=="{{PageSeeAlso}}"):
            break

        if(fc in topics):
            current_topic = fc 
            i += 1
            continue

        if(current_topic in ["{{PageParameters}}", "{{PageDescription}}", "{{PageAvailability}}"]):
            if(fc[:2]=="* "):
                fc = "\n- "+fc[2:]
            if(fc[:3]=="** "):
                fc = "\n- "+fc[3:]

        data[current_topic] += removeHTMLSpecialChars(fc)
        i += 1

    data["use"] = reformatStr(data["use"], True)
    
    data["{{PageSyntax}}"] = '`' + reformatStr(data["{{PageSyntax}}"][1:].replace("'''", "").replace("''", "")) + '`'
    data["{{PageParameters}}"] = reformatStr(data["{{PageParameters}}"], True).replace("'''", "").replace("''", "")
    data["{{PageDescription}}"] = reformatStr(data["{{PageDescription}}"], True).replace("'''", "").replace("''", "")
    
    data["bytes"] = len(data["title"]) + len(data["use"]) + len(data["{{PageSyntax}}"]) + len(data["{{PageParameters}}"])
    data["bytes"] += len(data["{{PageDescription}}"]) + len(data["{{PageAvailability}}"])
    
    return data

def getExample(keyword):
    res = ">>> **{}** Example:-\n```vb\n{}\n```\n"

    file_content = getRawDataFromQB64Wiki(keyword)

    found = False
    #parse the contents
    pos1 = file_content.find("{{CodeStart}}")
    pos2 = file_content.find("{{CodeEnd}}")
    if(pos1!=-1 and pos2!=-1):
        code = removeHTMLSpecialChars(file_content[pos1+13:pos2])
        return res.format(keyword.upper(), reformatStr(code).replace("'''", "").replace("''", ""))
    else:
        return "No example available for **{}** at Qb64 Wiki.".format(keyword.upper())

#def updatePage(keyword):


#print(getExample(input()))
#print(getDocumentation(input()))
#print(getDocumentation(input())["description"])
