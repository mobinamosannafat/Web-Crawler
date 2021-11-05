import re
import os
import pickle
import requests

LIMIT = 20  # limit the count of sites to be retrieved
START = ["https://www.blogsky.com/posts"]  # where crawling stars
INDEX_FILE = "index_object.bin"

class Index:
    def __init__(self, starts, limit):
        self.dictionary = {}
        self.doc_id_map = {}
        self.urls = starts.copy()
        self.limit = limit

    def build_index(self):
        doc_id = 1
        for url in self.urls:
            if doc_id > self.limit:
                break
            try:
                html = requests.get(url).text
            except:
                print("Error in getting url", url)
                continue

            extracted_links = set(filter(lambda a: a.startswith("http"), re.findall(r"<a href=\"(.*?)\"", html)))
            self.urls += list(extracted_links)
            extracted_text = re.sub(r"<.*?>", "", html)
            words = filter(lambda a: len(a) >= 2, re.findall(r"\w+", extracted_text.lower()))
            self.doc_id_map[doc_id] = url
            print("Found", len(extracted_links), "links in", url)
            position = 1
            for word in words:
                if word in self.dictionary:
                    posting_list = self.dictionary[word]
                    if doc_id in posting_list:
                        posting_list[doc_id].append(position)
                        position = position + 1
                    else:
                        posting_list[doc_id] = [position]
                        position = position + 1
                else:
                    self.dictionary[word] = {doc_id: [position]}
                    position = position + 1

            doc_id = doc_id + 1

    def final_print(self, item):
        print("<<", self.doc_id_map[item], ">>")

    def and_query(self, query_terms):
        if len(query_terms) == 1:
            result_list = self.get_posting_list(query_terms[0])
            if not result_list:
                print("\nResult for the Query: ", query_terms[0])
                print("0 documents returned as there is no match")
                return

            else:
                print("\nResult for the Query:", query_terms[0])
                print("Total documents retrieved:", len(result_list))
                for items in result_list:
                    # print (self.doc_id_map[items]) 
                    self.final_print(items)

        else:
            result_list = []
            for i in range(1, len(query_terms)): 
                if len(result_list) == 0:
                    result_list = self.merge_posting_list(
                        self.get_posting_list(query_terms[0]), self.get_posting_list(query_terms[i])
                    )
                else:
                    result_list = self.merge_posting_list(result_list, self.get_posting_list(query_terms[i]))

            print_string = "\nResult for the Query(AND query):"
            i = 1
            for keys in query_terms:
                if i == len(query_terms):
                    print_string += " " + str(keys)
                else:
                    print_string += " " + str(keys) + " AND"
                    i = i + 1

            print(print_string)
            print("Total documents retrieved:", len(result_list))
            for items in result_list:
                # print (self.doc_id_map[items])
                self.final_print(items)

    def get_posting_list(self, term):
        if term in self.dictionary:
            posting_list = self.dictionary[term]
            keys_list = []
            for keys in posting_list:
                keys_list.append(keys)
            keys_list.sort()
            # print keys_list
            return keys_list
        else:
            return None

    def merge_posting_list(self, list1, list2):
        merge_result = list(set(list1) & set(list2))
        merge_result.sort()
        return merge_result


def make_index():
    index_object = Index(starts=START, limit=LIMIT)
    index_object.build_index()
    pickle.dump(index_object, open(INDEX_FILE, "wb+"), pickle.HIGHEST_PROTOCOL)
    return index_object


def load_index():
    index_object = pickle.load(open(INDEX_FILE, "rb"))
    return index_object


def main():
    if os.path.exists(INDEX_FILE):
        index_object = load_index()
    else:
        index_object = make_index()

    while True:
        query = input("Enter query (or type exit): ")
        if query == "exit":
            break

        index_object.and_query(re.findall("\w+", query.lower()))

    print("Thank you for using this program")


if __name__ == "__main__":
    main()
