# fintechapp

For this project, I used the IBM Watson Natural Language Understanding API. They had many features, but I chose Keyword, Sentiment, and Relations Analysis. I have designed this app such that it will take in any valid ticker input and display the results. In order to get it completely working, you might need to create an IBM Watson NLU account to get your own API key and URL. I do not plan to display mine publicly. It utilizes Flask and HTML as its primary stack. This is a simple architecture that I am comfortable with using.

Keyword:
Analyzing keywords helps optimize for SEO, thus proving important for potential economic opportunity. I used a bubble scatter chart to display the relevance, Gunning-Fog index (which is not a totally helpful statistic, but my logic was that since it measures the simplicity of a text, it is useful for SEO analysis), and the count of the word in the text.

Sentiment:
Analyzing the sentiment can potentially allow a user to look at whether the year was successful. If I'm not mistaken, I believe the IBM API provides a score that measures positive sentiment. From here, the user could potentially which years did better than other years.

Relation:
This relational analysis is also important for SEO analysis and a general understanding of the different interactions that exist within the text. This data is displayed using a knowledge graph.

The following video is the app in action. Please note that it takes a long time for the API to process the data, so feel free to skip to the end to see the results. I used data from Johnson & Johnson.

https://github.com/jthomas462/fintechapp/assets/123043891/dc3c8b76-557f-4ed1-9174-eef0d22968be

