# Web Crawler

A web crawler that indexes accessible sites by getting a set of primary URLs.

The crawler works in such a way that first extracts several links in the initial link, as large as the "limit" variable we specify, and separates their texts. It then examines all the texts and creates a dictionary for their words. This dictionary is stored as a .txt file so that it can be used for Boolean retrieval if the user searches. To search, the mentioned file will be used to display the list of all documents that contain all the words in the user query to the user.
