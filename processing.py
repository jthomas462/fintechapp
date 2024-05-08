from sec_edgar_downloader import Downloader
import os
import re
import json
from dotenv import load_dotenv
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import \
        Features, KeywordsOptions, SentimentOptions, RelationsOptions
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import textstat
import networkx as nx

class Processing:
    def __init__(self, ticker):
        self.ticker = ticker
        print("In Processing class")
        self.main()
    
    def main(self):
        folder_path = self.validate_and_download()
        my_dict = self.clean_text(folder_path)
        keywords, sentiment, relations, responses = self.nlp_analysis(my_dict)
        self.visualize(keywords, sentiment, relations, responses)
    
    def validate_and_download(self):
        # this method uses the ticker symbol and downloads the relevant 10-K files from the sec-edgar-downloader library
        # it returns the folder path
        print("validate and download method accessed")
        dl = Downloader("Jonathan", "jonathanthom145@gmail.com")
        current_directory = os.getcwd()
        try:
            dl.get("10-K", self.ticker)
        except:
            return "Invalid ticker. Please check to make sure ticker exists"
        folder_path = current_directory + '\\sec-edgar-filings\\' + self.ticker + '\\10-K'
        return folder_path

    def clean_text(self, folder_path):
        # this method cleans the text using regex. It loops through each file in the downloaded folders and stores
        # the text in a dict.
        print("clean text method accessed")
        my_dict = {}
        folders = os.listdir(folder_path)
        for file in folders:
            file_path = folder_path + "/" + file + "/" + "full-submission.txt"
            with open(file_path, "r", encoding = "utf-8") as new_file:
                text = new_file.read()
                cleaned_text = re.compile(r'<[^>]+>').sub('', text)
                year_to_be = re.findall(r'-\d{2}-', file_path)
                year = year_to_be[0][1:3]
                # ChatGPT
                print(year)
                my_dict.update({ year : cleaned_text })
        return my_dict

    def nlp_analysis(self, my_dict):
        # this method uses the IBM Watson Natural Language Understanding API to return 
        # the keywords, sentiment, and relations found in a text for all the 10-Ks
        # it returns them as dicts
        print("nlp_analysis method accessed")
        load_dotenv()
        auth = IAMAuthenticator(os.environ.get('API_KEY'))
        nlu = NaturalLanguageUnderstandingV1('2022-04-07', authenticator = auth)

        nlu.set_service_url(os.environ.get('URL'))

        responses = {}

        for key in my_dict:
            print(key)
            res = nlu.analyze(
            text = my_dict[key],
        
            features = Features(keywords = KeywordsOptions(), \
                                 sentiment = SentimentOptions(), \
                                 relations = RelationsOptions())
            ).get_result()
            responses.update({ key : res})

        print("safe")
        keywords = [response.get('keywords') for response in responses.values()]
        sentiment = [response.get('sentiment') for response in responses.values()]
        relations = [response.get('relations') for response in responses.values()]
        # for key in responses.keys():
        #     print(key)
        print("safe_2")
        return keywords, sentiment, relations, my_dict

    def visualize(self, keywords, sentiment, relations, responses):
        # this method calls three helper methods to visualize the data
        print("visualize method accessed")
        self.k_visualize(keywords, responses)
        self.s_visualize(sentiment, responses)
        self.r_visualize(relations, responses)

    def k_visualize(self, keywords, responses):
        print("k method accessed")
        text = [d['text'] for d in keywords[0]]
        relevance = [d['relevance'] for d in keywords[0]]
        count = [d['count'] for d in keywords[0]]
        gunning_fog = [textstat.gunning_fog(t) for t in text]

        keyword_data = pd.DataFrame({'text': text, 'relevance': relevance, 'count': count, 'gunning_fog': gunning_fog})
        keyword_data = keyword_data.sort_values(by = "count", ascending=False)
        keyword_data = keyword_data[keyword_data['text'] != 'nbsp']


        keyword_fig = px.scatter(keyword_data, x = "relevance", y = "gunning_fog", size = "count", hover_name = "text")
        keyword_fig.show()
    
    def s_visualize(self, sentiment, responses):
        print("s method accessed")
        
        # print(responses.keys())
        to_be_mod =  [("19" + key) if int(key) >= 94 else ("20" + key) for key in responses.keys()]
        # ChatGPT
        year = [int(res) for res in to_be_mod]
        sentiment_data = pd.DataFrame({'year' : year, 'positive_score' : [sent["document"]["score"] for sent in sentiment]})
        data = sentiment_data.sort_values(by = 'year', ascending = True)
        print(data)

        sentiment_fig = px.bar(data, x = 'year', y = 'positive_score', title = 'Positivity Sentiment Score Over Years 1994-2024' + ' (' + self.ticker + ')')
        sentiment_fig.show()
    
    def r_visualize(self, relations, responses):
        print("r method accessed")
        predicate = [d['type'] for d in relations[0]]
        subject_to_be = [d['arguments'] for d in relations[0]]
        subject = []
        objectp = []
        for i in subject_to_be:
            subject.append(i[0]['text'])
            objectp.append(i[1]['text'])
        relations_data = pd.DataFrame({'subject': subject, 'predicate': predicate, 'object': objectp})

        G = nx.Graph()
        for _, row in relations_data.iterrows():
            G.add_edge(row['subject'], row['object'], label=row['predicate'])

        pos = nx.spring_layout(G, seed = 42, k = 0.9)

        edge_trace = []
        for edge in G.edges(data=True):
            edge_trace.append(go.Scatter(x=[pos[edge[0]][0], pos[edge[1]][0], None],
                                        y=[pos[edge[0]][1], pos[edge[1]][1], None],
                                        line=dict(width=0.5, color='#888'),
                                        hoverinfo='none',
                                        mode='lines'))

        node_trace = go.Scatter(x=[],
                                y=[],
                                text=[],
                                mode='markers',
                                hoverinfo='text',
                                marker=dict(color=[],
                                            size=10,
                                            line=dict(width=2)))

        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (node,)

        fig = go.Figure(data=edge_trace + [node_trace],
                        layout=go.Layout(title='<br>Knowledge Graph',
                                        titlefont_size=16,
                                        showlegend=False,
                                        hovermode='closest',
                                        margin=dict(b=20, l=5, r=5, t=40),
                                        annotations=[dict(
                                            text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                                            showarrow=False,
                                            xref="paper", yref="paper",
                                            x=0.005, y=-0.002)],
                                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        fig.show()

        # Source: https://lopezyse.medium.com/knowledge-graphs-from-scratch-with-python-f3c2a05914cc, ChatGPT

