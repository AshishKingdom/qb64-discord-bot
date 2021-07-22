# @Author : AshishKingdom (Ashish Kushwaha)

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

    data = {"title":keyword.upper(), "use":"", "syntax":"", "parameters":"", "description":"", "availability":""}

    file_content = getRawDataFromQB64Wiki(keyword).split('\n')

    #parse the contents
    done_use = False
    for i in range(0, len(file_content)):
        if(done_use==False):
            if(file_content[0][:15]=="{{DISPLAYTITLE:"):
                j = 1
            else:
                j = 0
            while(file_content[j].strip()!=''):
                data["use"] += removeHTMLSpecialChars(file_content[j])+' '
                j += 1
            done_use = True
        fc = file_content[i].strip()

        if(fc=="{{PageSyntax}}"):
            data["syntax"] = removeHTMLSpecialChars(file_content[i+1][1:])
        if(fc=="{{PageParameters}}"):
            j = i+1
            while(file_content[j].strip()!=''):
                data["parameters"] += "- " + removeHTMLSpecialChars(file_content[j][2:])+'\n'
                j += 1
        if(fc=="{{PageDescription}}"):
            j = i+1
            k = 2
            while(file_content[j].strip()!=''):
                if(file_content[j][:14]=="{{WhiteStart}}"): 
                    k = 0
                    data["description"] += "\n```\n"
                    j += 1
                if(file_content[j][:12]=="{{WhiteEnd}}"):
                    k = 2
                    data["description"] += "\n```\n"
                    j += 1
                if k==2:
                    data["description"] += "- " + removeHTMLSpecialChars(file_content[j][2:])+'\n'
                else:
                    data["description"] += removeHTMLSpecialChars(file_content[j])+'\n'
                j += 1
        if(fc=="{{PageAvailability}}"):
            data["availability"] = "- " + removeHTMLSpecialChars(file_content[i+1][2:])
        if(fc=="{{PageExamples}}" or fc=="{{PageSeeAlso}}"):
            break

    data["use"] = reformatStr(data["use"], True)
    data["syntax"] = '`' + replaceStr(reformatStr(data["syntax"]), "'''", '') + '`'
    data["parameters"] = replaceStr(reformatStr(data["parameters"], True), "'''", '')
    data["description"] = (reformatStr(data["description"], True)).replace("'''", "").replace("''", "")
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
