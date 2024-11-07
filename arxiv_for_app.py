import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from arxiv_api_integration_ai_connect import answer

def pdf_download(pdf_link, article_title):
    # 根据返回的PDF下载连接，下载 PDF 文件
    pdf_filename = article_title + ".pdf"
    urllib.request.urlretrieve(pdf_link, pdf_filename)

def arxiv_api_calling(article_title, translation):
    # 定义参数
    method_name = "query"
    start = 0
    max_results = 29

    # 对参数进行编码
    encoded_article_title = urllib.parse.quote(article_title)

    # 构建有效的 URL
    url = f"http://export.arxiv.org/api/{method_name}?search_query={encoded_article_title}&start={start}&max_results={max_results}"

    # 获取数据
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')

    # 解析 XML 数据
    root = ET.fromstring(data)

    # 提取文章信息
    article = {}
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        if entry.find('{http://www.w3.org/2005/Atom}title').text == article_title:
            article['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text if entry.find('{http://www.w3.org/2005/Atom}id') is not None else 'No ID available'
            article['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text[:10] if entry.find('{http://www.w3.org/2005/Atom}updated') is not None else 'No update date available'
            article['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text[:10] if entry.find('{http://www.w3.org/2005/Atom}published') is not None else 'No publish date available'
            article['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else 'No title available'
            article['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text if entry.find('{http://www.w3.org/2005/Atom}summary') is not None else 'No summary available'
            
            authors = entry.findall('{http://www.w3.org/2005/Atom}author')
            article['authors'] = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors] if authors else ['No authors available']
            
            pdf_link = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]')
            article['pdf_link'] = pdf_link.attrib['href'] if pdf_link is not None else 'N/A'

    if 'summary' in article:
        summarized_article = answer(article['summary'], translation)
        article['summarized summary'] = summarized_article

        # 调用函数，下载 PDF 文件
        try:
            pdf_download(article['pdf_link'], article['title'])
            print(f"PDF downloaded successfully as {article['title']}.pdf .")
        except Exception as e:
            raise Exception(f"Download Fail: {e}")

    return article
