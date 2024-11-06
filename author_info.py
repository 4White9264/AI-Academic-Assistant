import requests
import json
import sys
from serpapi import GoogleSearch

# 读取配置文件的函数
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value
    return config

# 获取作者信息的函数
def get_author_info(name, config):
    params = {
        "engine": "google_scholar",
        "q": name,
        "api_key": config['SERPAPI_API_KEY']
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    search_link = results.get('search_metadata', {}).get('google_scholar_url', 'N/A')
    if "error" in results:
        print(f"Error: {results['error']}")
        return None
    
    if "profiles" not in results or "authors" not in results["profiles"]:
        print("No author found for the given name.")
        return None
    
    author = results["profiles"]["authors"][0]
    author_info = {
        "name": author.get('name', 'N/A'),
        "affiliation": author.get('affiliations', 'N/A'),
        "email": author.get('email', 'N/A'),
        "interests": author.get('interests', 'N/A'),
        "position": author.get('position', 'N/A'),
        "research_areas": author.get('research_areas', 'N/A'),
        "top3_publications": [pub.get('title', 'N/A') for pub in author.get('publications', [])[:3]],
        "google_scholar_profile": author.get('link', 'N/A'),
        "search_link": search_link
    }
    
    return author_info

# 获取个人主页的前三篇文章和其他信息
def get_additional_info(author_url, config):
    author_id = author_url.split('user=')[1].split('&')[0]
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": config['SERPAPI_API_KEY']
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if "error" in results:
        print(f"Error: {results['error']}")
        return None
    
    publications = results.get("articles", [])
    # 根据被引用次数排序，处理None值
    sorted_publications = sorted(publications, key=lambda x: x.get('cited_by', {}).get('value', 0) or 0, reverse=True)
    top3_publications = [{"title": pub.get('title', 'N/A'), "link": pub.get('link', 'N/A'), "cited_by": pub.get('cited_by', {}).get('value', 0)} for pub in sorted_publications[:3]]
    
    additional_info = {
        "position": results.get('position', 'N/A'),
        "research_areas": results.get('research_areas', 'N/A'),
        "top3_publications": top3_publications
    }
    
    return additional_info

# 使用AI对输出进行总结
def summarize_output(output, config):
    OPENROUTER_API_KEY = config['OPENROUTER_API_KEY']
    YOUR_SITE_URL = config.get('YOUR_SITE_URL', 'your_site_url_here')
    YOUR_APP_NAME = config.get('YOUR_APP_NAME', 'your_app_name_here')
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": YOUR_SITE_URL,  # Optional, for including your app on openrouter.ai rankings.
            "X-Title": YOUR_APP_NAME,  # Optional. Shows in rankings on openrouter.ai.
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "meta-llama/llama-3.2-1b-instruct:free",  # Optional
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize the following author information in a single paragraph with 'Name: Content' format, omitting any fields that are 'N/A': {output}"
                }
            ]
        })
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"API 请求失败，状态码: {response.status_code}, 错误信息: {response.json()}")

# 示例调用
if __name__ == "__main__":
    config = read_config('config.txt')
    
    if len(sys.argv) < 2:
        print("Usage: python author_info.py <author_name>")
        sys.exit(1)
    
    author_name = sys.argv[1]
    
    print(f"Retrieving information for author: {author_name}")
    author_info = get_author_info(author_name, config)
    if author_info:
        output = "Author Info:\n"
        for key, value in author_info.items():
            if value != 'N/A':
                output += f"{key}: {value}\n"
        
        additional_info = None
        if author_info["google_scholar_profile"] != 'N/A':
            additional_info = get_additional_info(author_info["google_scholar_profile"], config)
            if additional_info:
                output += "\nAdditional Info:\n"
                for key, value in additional_info.items():
                    if key == "top3_publications":
                        output += "\nTop 3 Publications:\n"
                        for pub in value:
                            output += f"Title: {pub['title']}, Link: {pub['link']}, Cited by: {pub['cited_by']}\n"
                    elif value != 'N/A':
                        output += f"{key}: {value}\n"
            else:
                output += "Error retrieving additional information\n"
        
        print(output)
        
        try:
            summary = summarize_output(output, config)
            print("\nSummary:\n")
            print(summary)
        except Exception as e:
            print(f"Error summarizing output: {e}")
    else:
        print("Error retrieving author information")

# 获取作者ID的函数
def get_author_id(name, config):
    params = {
        "engine": "google_scholar_profiles",
        "mauthors": name,
        "api_key": config['SERPAPI_API_KEY']
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    profiles = results.get("profiles", [])
    if profiles:
        return profiles[0].get("author_id", None)
    return None

# 获取作者详细信息的函数，包括h-index、i10-index和被引用次数
def get_author_details(author_id, config):
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": config['SERPAPI_API_KEY']
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results

# 计算评分的函数
def calculate_scores(h_index, i10_index, total_citations):
    h_index_score = (h_index / 50) * 100 * (1/3) if h_index != "N/A" else 0
    i10_index_score = (i10_index / 150) * 100 * (1/3) if i10_index != "N/A" else 0
    total_citations_score = (total_citations / 10000) * 100 * (1/3) if total_citations != "N/A" else 0
    total_score = h_index_score + i10_index_score + total_citations_score
    return h_index_score, i10_index_score, total_citations_score, total_score

# 示例调用
if __name__ == "__main__":
    config = read_config('config.txt')
    
    if len(sys.argv) < 2:
        print("Usage: python test.py <author_name>")
        sys.exit(1)
    
    author_name = sys.argv[1]
    
    print(f"Retrieving information for author: {author_name}")
    author_id = get_author_id(author_name, config)
    if author_id:
        author_details = get_author_details(author_id, config)
        if author_details:
            interests = author_details.get("interests", [])
            cited_by = author_details.get("cited_by", {}).get("table", [])
            
            h_index = "N/A"
            i10_index = "N/A"
            total_citations = "N/A"
            
            for item in cited_by:
                if item.get("citations", {}).get("all", "N/A") != "N/A":
                    total_citations = item["citations"]["all"]
                if item.get("h_index", {}).get("all", "N/A") != "N/A":
                    h_index = item["h_index"]["all"]
                if item.get("i10_index", {}).get("all", "N/A") != "N/A":
                    i10_index = item["i10_index"]["all"]
            
            interests_formatted = ", ".join([interest.get("title", "N/A") for interest in interests])
            
            print(f"Interests: {interests_formatted}")
            print(f"h-index: {h_index}")
            print(f"i10-index: {i10_index}")
            print(f"Cited by: {total_citations}")
            
            # 计算评分
            h_index_score, i10_index_score, total_citations_score, total_score = calculate_scores(h_index, i10_index, total_citations)
            
            print(f"\nh-index Score: {h_index_score:.2f}")
            print(f"i10-index Score: {i10_index_score:.2f}")
            print(f"Total Citations Score: {total_citations_score:.2f}")
            print(f"Total Score: {total_score:.2f}")
            print("\n")
        else:
            print("Error retrieving author information")
    else:
        print("Author ID not found")