import streamlit as st
import arxiv
import requests
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

st.title("🧠 Discover Research Insights & Trends")
st.write("Type a topic to find papers, patents, and market buzz!")

# Step 1: Enter Query
query = st.text_input("Enter your query (e.g., 'AI robots'):", "quantum computing")

if st.button("🚀 Find Insights!") and query:
    with st.spinner("Gathering treasures..."):
        
        # Aggregate: Papers from arXiv
        st.subheader("📚 Academic Papers (arXiv)")
        papers = []
        try:
            search = arxiv.Search(query, max_results=10)
            for result in search.results():
                papers.append({
                    'Title': result.title,
                    'Authors': ', '.join(author.name for author in result.authors),
                    'Date': str(result.published),
                    'Summary': result.summary[:200] + '...',
                    'PDF': result.pdf_url
                })
            papers_df = pd.DataFrame(papers)
            st.dataframe(papers_df, use_container_width=True)
        except:
            st.write("No papers found. Try another query!")
        
        # Aggregate: Patents (PatentsView API)
        st.subheader("🔬 Patents")
        patents = []
        try:
            url = f"https://api.patentsview.org/patents/query?q={{{{_text_any:{{{{'{query}'}}}}}}&f=[['patent_id','patent_title','patent_date']]&o={{{{page:0,size:10}}}}"
            resp = requests.get(url).json()
            for p in resp['patents']:
                patents.append({
                    'ID': p['patent_id'],
                    'Title': p.get('patent_title', 'N/A'),
                    'Date': p.get('patent_date', 'N/A')
                })
            patents_df = pd.DataFrame(patents)
            st.dataframe(patents_df, use_container_width=True)
        except:
            st.write("No patents found.")
        
        # Aggregate: Market Trends (Google Trends)
        st.subheader("📈 Market Trends")
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([query], cat=0, timeframe='today 12-m', geo='')
            df_trends = pytrends.interest_over_time()
            if not df_trends.empty:
                fig = px.line(df_trends, x=df_trends.index, y=query, title=f"Interest in '{query}' over time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No trend data.")
        except:
            st.write("Trends unavailable.")
        
        # Analyze: Simple stats & Word Cloud
        st.subheader("🔍 Quick Analysis")
        total_items = len(papers) + len(patents)
        st.metric("Total Insights Found", total_items)
        
        # Word cloud from titles
        all_text = ' '.join([p.get('Title', '') for p in papers + patents])
        if all_text:
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        
        # Export & Share
        df_all = pd.concat([papers_df, patents_df], ignore_index=True, sort=False) if 'papers_df' in locals() and 'patents_df' in locals() else pd.DataFrame()
        csv = df_all.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export CSV", csv, f"{query}_insights.csv", "text/csv")
        st.info("💡 Share this app: [Your App Link after deploy]")

else:
    st.info("👆 Type a query and click the button!")
