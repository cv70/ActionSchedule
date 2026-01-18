import time
from bs4 import BeautifulSoup
import requests


def get_huggingface_papers(num_papers=5):
    # 目标URL
    url = "https://huggingface.co/papers"
    
    try:
        # 发送HTTP请求 
        response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # 检查请求是否成功
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 初始化结果列表
        papers = []
        
        # 查找包含论文信息的元素
        # 根据页面结构，论文条目通常在<article>标签或特定class的<div>中
        # 这里使用更通用的选择器，可能需要根据实际页面结构调整
        paper_elements = soup.find_all('article', limit=num_papers)
        
        # 如果找不到<article>标签，尝试其他选择器
        if not paper_elements:
            paper_elements = soup.select('[data-target="paper-card"]', limit=num_papers)
        
        # 如果还找不到，尝试查找具有论文特征的div
        if not paper_elements:
            paper_elements = soup.select('div[class*="paper"], div[class*="card"]', limit=num_papers)
        
        # 提取每个论文的信息
        for i, element in enumerate(paper_elements[:num_papers]):
            try:
                # 提取论文标题
                title_element = element.find(['h3', 'h4', 'a'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['title', 'heading', 'name']))
                if not title_element:
                    title_element = element.find(['h3', 'h4', 'a'])
                
                title = title_element.get_text(strip=True) if title_element else "标题未找到"
                
                # 提取论文链接
                link_element = element.find('a', href=True)
                if link_element:
                    link = link_element['href']
                    # 确保链接完整
                    if link.startswith('/'):
                        link = f"https://huggingface.co{link}"
                else:
                    link = "链接未找到"
                
                # 提取论文摘要/内容
                content_element = element.find(['p', 'div'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['abstract', 'summary', 'content', 'description']))
                if not content_element:
                    # 尝试查找第一个段落
                    content_element = element.find('p')
                
                content = content_element.get_text(strip=True) if content_element else "内容未找到"
                
                # 创建论文信息字典
                paper_info = {
                    'id': i + 1,
                    'title': title,
                    'content': content[:500] + "..." if len(content) > 500 else content,  # 限制内容长度
                    'link': link,
                }
                
                papers.append(paper_info)
                print(f"  已提取论文 {i+1}: {title[:50]}...")
                
                # 添加延迟以避免请求过快
                time.sleep(1)
                
            except Exception as e:
                print(f"  处理第 {i+1} 个论文元素时出错: {str(e)}")
                continue
        
        
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求出错: {e}")
        return []
    except Exception as e:
        print(f"程序执行出错: {e}")
        return []
    
papers = get_huggingface_papers()
print(papers)
