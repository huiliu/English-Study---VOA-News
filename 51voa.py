#!/bin/env python2

from BeautifulSoup import BeautifulSoup
import re
try:
    from urllib import urlopen
except Exception:
    from urllib.request import urlopen
import sqlite3

db_file = 'voa.db'

def ProgramList(url, tb_name, cur):

    reg_document = re.compile('<!DOCTYPE.*?>')

    #html_data = open('Health_Report_1.html').read()
    html_data = urlopen(url).read().decode('utf-8')
    html_data = reg_document.sub('', html_data)

    soup = BeautifulSoup(html_data)
    span = soup.find('span', {"id":"list"})

    ii = 0
    # Get the Program List
    Health_Report_List = []
    for i in span.findAll('li'):
        a = i.find('a')
        # How could be setup the Dict quickly?
        # tmp = {}
        # tmp['title'] = a.string
        # tmp['href'] = 'http://www.51voa.com' + a['href']
        title = a.string
        url =  'http://www.51voa.com' + a['href']
        print(title)
        GetProgramContent(title, tb_name, url, cur)
        #Health_Report_List.append(tmp)
        if ii > 5: break
        ii += 1

    return Health_Report_List

def GetProgramContent(title, tb_name, url, cur):
    """This function use to get the content of the program,
    contain origin material text, mp3, lrc, translation.

    title           the title of the program
    url             the url of page
    """

    reg_strong = re.compile('<?strong>')
    reg = re.compile('<.*?>')

    reg_document = re.compile('<!DOCTYPE.*?>')
    html_data = urlopen(url).read().decode('utf-8')
    html_data = reg_document.sub('', html_data)

    soup = BeautifulSoup(html_data)

    title = title.replace("'", "''")
    title = title.replace('"','""')

    div_menubar = soup.find('div', {'id':'menubar'})
    a = div_menubar.findAll('a')
    mp3 = 'http://www.51voa.com' + a[0]['href']
    lrc = ''
    trans = ''
    if len(a) == 4:
    # This Program contain mp3, lyc, tran
        lrc = 'http://www.51voa.com' + a[1]['href']
        trans = 'http://www.51voa.com/VOA_Special_English/' \
            + a[2]['href']
        #print(trans)
        # Save the Translation to file
        getTrans(trans, title+'.trans')
    elif len(a) == 3:
    # This Program May be just contain mp3, tran
        lrc = 'http://www.51voa.com' + a[1]['href']

    savefile(mp3, title + '.mp3', flags=2)
    savefile(lrc, title + '.lrc', flags=2)

    text = purifyContent(soup)
    savefile(text, [tb_name, title,'',''], cur)

def getTrans(url, filename):
    """This function use to get the translation content.
    And no return value.

    url             the url of trans page
    filename        the name of file use to save translation
    """

    # Delete The Tag <!DOCTYPE ......>
    reg_document = re.compile('<!DOCTYPE.*?>')
    data = urlopen(url).read().decode('utf-8')
    data = reg_document.sub('', data)

    soup = BeautifulSoup(data)
    text = purifyContent(soup)
    savefile(text, filename, flags=1)

def purifyContent(soup):
    """This function use to purify the Program text content
    which contain some HTML sybaml.

    soup            the BeautifulSoup object content the text content
    """

    reg_strong = re.compile('<?strong>')
    reg = re.compile('<.*?>')

    div_content = soup.find('div', {'id':'content'})
    for i in div_content.findAll('div'):
        i.extract()
    # print(div_content)
    #content =  reg.sub('\n', reg_strong.sub('', str(div_content).decode('utf-8')))
    content =  re.sub('\n{1,}', '\n',str(div_content).decode('utf-8'))

    return content
    """
    if cur != '':
        artical = [title, content, '', '']
        #Insert2DB(artical, 'economics', cur)
    else:
        artical = content
    """

def savefile(url, other_data, cur='', flags=0):
    """This function use to save the download file.
    url             the url of media file or text file
    other_data      a list contain [tbname,filetype,pubtime]
    cur             the name of file use to save the download content
    """
    if flags == 0:
    # Save material into Database
        data = url
        data = data.replace("'", "''")
        data = data.replace('"','""')

        sql_insert = "INSERT INTO %s VALUES('%s', '%s', '%s', '%s')"%(other_data[0], other_data[1], data, other_data[2], other_data[3])
        cur.execute(sql_insert)
        return 0
    elif flags == 1:
    # Save mp3, lyr to file
        data = url
    else:
        data = urlopen(url).read()

        f = open(other_data, 'w')
        f.write(data)
        f.close()

def CreateTable(db, tbname):
    """
    """
    # --------- Create DataBase ----------
    create_DB = "CREATE TABLE %s (title text,content text, ftype varchar(3), publish date)" %(tbname)
    try:
        db.execute(create_DB)
    except sqlite3.Error:
        pass

def Insert2DB(item, tname, cur):
    """
    """
    #print(item)
    insert_DB = 'INSERT INTO %s VALUES("%s", "%s", "%s","%s")' % (tname, item[0], item[1], item[2], item[3])
    # Escape "
    #print insert_DB
    cur.execute(insert_DB)

if __name__ == '__main__':

    education_db = 'education'

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    CreateTable(cur, education_db)

    economics_report_url = 'http://www.51voa.com/Economics_Report_1.html'
    Education_report_url = 'http://www.51voa.com/Education_Report_1.html'
    ProgramList(Education_report_url, education_db, cur)

    conn.commit()
    cur.close()
