import streamlit as st
from input import Section_A_output, Section_B_output, Section_D_output

def display_article_details(article):
    with st.expander(article.get('title', 'N/A')):
        st.subheader("Article Information")
        st.write(f"**Link:** {article.get('link', 'N/A')}")
        st.write(f"**Summary:** {article.get('summary', 'N/A')}")
        st.write(f"**Snippet:** {article.get('snippet', 'N/A')}")
        st.write(f"**PDF Link:** {article.get('pdf link', 'N/A')}")
        st.write(f"**Summarized Summary:** {article.get('summarized summary', 'N/A')}")

        st.subheader("Publication Details")
        st.write(f"**Published:** {article.get('published', 'N/A')}")
        st.write(f"**Updated:** {article.get('updated', 'N/A')}")
        st.write(f"**Journal:** {article.get('journal', 'N/A')}")
        st.write(f"**Cited By:** {article.get('cited_by', 'N/A')}")

        st.subheader("Authors")
        st.write(f"**Authors:** {', '.join(article.get('authors', []))}")
        author_info = article.get('author_info', {})
        if author_info:
            st.write(f"**Name:** {author_info.get('name', 'N/A')}")
            st.write(f"**Affiliation:** {author_info.get('affiliation', 'N/A')}")
            st.write(f"**Email:** {author_info.get('email', 'N/A')}")
            top3_publications = author_info.get('top3_publications', [])
            if top3_publications:
                for pub in top3_publications:
                    st.write(f"**Publication Title:** {pub.get('title', 'N/A')}")
                    st.write(f"**Link:** {pub.get('link', 'N/A')}")

# 從 input.py 中獲取文章資料
article = {
    'title': Section_A_output.get('title', 'N/A'),
    'link': Section_A_output.get('link', 'N/A'),
    'summary': Section_A_output.get('summary', 'N/A'),
    'snippet': Section_A_output.get('snippet', 'N/A'),
    'pdf link': Section_D_output.get('pdf link', 'N/A'),
    'summarized summary': Section_D_output.get('summarized summary', 'N/A'),
    'published': Section_D_output.get('published', 'N/A'),
    'updated': Section_D_output.get('updated', 'N/A'),
    'journal': Section_A_output.get('journal', 'N/A'),
    'cited_by': Section_A_output.get('cited_by', 'N/A'),
    'authors': Section_D_output.get('authors', []),
    'author_info': Section_A_output.get('author_info', {})
}

# 呼叫函數顯示文章詳細資訊
display_article_details(article)