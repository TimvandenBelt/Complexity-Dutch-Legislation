import spacy
from spacy_syllables import SpacySyllables
nlp = spacy.load('nl_core_news_lg')
nlp.add_pipe("syllables", after="tagger")


class Legal_node:
    id: str
    type: str
    label: str
    text_list: list
    text_string: str
    num_tokens: int
    word_list: list
    word_list_with_lemma_without_stopwords: list
    word_list_with_lemma_with_stopwords: list
    word_list_without_stopwords: list
    number_of_words_without_stopwords: int
    number_of_words_with_stopwords: int
    avg_sentence_length = int
    avg_sentence_length_without_stopwords = int
    avg_word_length = int
    avg_syllable_length = int
    word_length_list = list
    syllable_lengths_list = list
    num_sentences = int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def __init__(self, id, type, label, text=None):
        self.id = id
        self.type = type
        self.label = label

        if text is not None:
            self.text_string = " ".join(text)
            self.text_list = text
        else:
            self.text_string = None
            self.text_list = None

        if self.is_text_node():
            """ Initialize all variables and call the proccess_text function """
            self.init_vars()
            self.proccess_text()
            self.calculate_stats()

    def init_vars(self):
        self.num_tokens = 0
        self.word_list = []
        self.word_list_with_lemma_without_stopwords = []
        self.word_list_with_lemma_with_stopwords = []
        self.word_list_without_stopwords = []
        self.numWordsWithoutStop = 0
        self.numWordsWithStop = 0
        self.numSentences = 0
        self.avg_sentence_length = 0
        self.avg_sentence_length_without_stopwords = 0
        self.avg_word_length = 0
        self.avg_syllable_length = 0
        self.word_length_list = []
        self.syllable_lengths_list = []
        self.num_sentences = 0

    def t(self):
        return self.text_string

    def is_text_node(self):
        if self.text_string is not None and not self.text_string == "":
            return True
        return False

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_label(self):
        return self.type + " - " + self.label

    def calculate_stats(self):
        self.number_of_words_without_stopwords = len(
            self.word_list_with_lemma_without_stopwords)
        self.number_of_words_with_stopwords = len(self.word_list)

        """ The issue only arrises in two acts. One has only numbers as content but with some markup invisible for the human eye. The other one is empty content for the human eye, but with some markup. Last one is I assume an error in the dataset. """
        try:
            """ If syllable length is not empty, calculate the average syllable length """
            if len(self.syllable_lengths_list) > 0:
                self.avg_syllable_length = sum(
                    self.syllable_lengths_list) / len(self.syllable_lengths_list)
            else:
                self.avg_syllable_length = 0
            self.avg_word_length = sum(
                self.word_length_list) / len(self.word_length_list)
            self.avg_sentence_length /= self.num_sentences
            self.avg_sentence_length_without_stopwords /= self.num_sentences
        except Exception as e:
            pass
            # print("No sentences found")

    def proccess_text(self):
        """ Use spaCy NLP to process the text and extract relevant information """
        doc = nlp(self.text_string)

        """ Loop over all the tokens of the text string """
        for token in doc:

            """ We do not care for numbers, punctuation, spaces or brackets """
            if token.is_punct or token.is_space or token.is_bracket:
                continue

            """ Token is a valid token, increment the amount"""
            self.num_tokens += 1

            """ The rest is only for words """
            if token.is_digit:
                continue

            """ Get the length of the word and append the length to the word_length_list """
            self.word_length_list.append(len(token.text))

            """ Get the text of the word and append it to the word_list """
            self.word_list.append(token.text)

            """ Get the lemmatized text of the word and append it to word_list_with_lemma_with_stopwords """
            self.word_list_with_lemma_with_stopwords.append(token.lemma_)

            """ If the amount of syllables could be fetched, add the amount fo the syllable_lengths list """
            if token._.syllables_count is not None:
                self.syllable_lengths_list.append(token._.syllables_count)

            """ lists without stopwords """
            if not token.is_stop:
                self.word_list_with_lemma_without_stopwords.append(
                    token.lemma_)
                self.word_list_without_stopwords.append(token.text)

        """ Done with looping over all the tokens """

        """ Calculate the amount of sentences in the text and the avarage amount of words per sentence """
        for sentence in doc.sents:
            self.num_sentences += 1
            """ Get the amount of words in each sentence without stop words and without punctiation """
            word_amount_without_stop = 0
            word_amount_with_stop = 0
            for token in sentence:
                if token.is_punct:
                    continue
                word_amount_with_stop += 1
                if not token.is_stop:
                    word_amount_without_stop += 1
            self.avg_sentence_length_without_stopwords += word_amount_without_stop
            self.avg_sentence_length += word_amount_with_stop
