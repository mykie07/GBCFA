def sent_extract_engine():
    print("absapi sentiment extractor loaded......")



def get_parent(word_pos, tree_dict):
    '''
    Get parent of a particular node in tree graph
    '''
    parent=tree_dict[word_pos]['parent']
    return parent



def get_children(word_pos, tree_dict, word_list = [],  get_all = False):
    '''
    Gets all descendants of a certain node in tree graph
    '''
    # Get immediate children
    children = tree_dict[word_pos]['children']

    # If no children return an empty list
    if children == []:
        return word_list

    # If children exist add them to word list
    word_list += children

    # Call get children for each child. This will capture grand-children etc.
    if get_all == True:
        for child in children:
            get_children(child, word_list = word_list, get_all = True)

    # After all recursion return word_list
    return word_list


def get_adjacents(word_pos,tree_dict):
        '''
        Get adjacent words of a particular node on tree graph
        '''
        words = get_children(word_pos, tree_dict, word_list = [], get_all = False)
        if word_pos != 0:
            words.append(get_parent(word_pos, tree_dict))
        return words



def get_siblings(word_pos):
    '''
    Get siblings of a particular node on tree graph
    '''
    if word_pos == 0:
        return []
    else:
        parent = get_parent(word_pos)
        children = get_children(parent, word_list = [], get_all = False)
        siblings = list(set(children) - set([word_pos]))
        return siblings


    
    
def get_words_by_dist(word_pos,tree_dict, dist):
    '''
    Gets all words within a particular distance on tree graph
    '''
    from copy import copy
    # Initialize words
    if type(word_pos) == list:
        words = word_pos
    else:
        words = [word_pos]

    # iterate through distance and continue to add adjacents to the list
    for i in range(dist):
        # distance 0 takes a word and all of its siblings
        new_words = copy(words)
        for word in words:
            new_words += get_adjacents(word,tree_dict)
        words = list(set(new_words))

    return words
    
    
    
def find_all(a_str, sub):
    '''
    Find all matches of sub within a_str. Returns starting index of matches.
    '''
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches


def hello():
    print("I am Mykie")



def get_tree_dict(sentence,nlp):
        # Add word, level, and position to dictionary
          
    doc = nlp(sentence)
    
    tree_word_list =list(doc)
    tree_word_list    
        
    lca_matrix = doc.get_lca_matrix()    
        
    l=len(lca_matrix)
    tree_positions=list(range(l))
    tree_positions
        
    tree_dict = {}
    word_count = 0
    for word, pos in zip(tree_word_list, tree_positions):
        temp_dict = {}
    #     depth = len(pos)
        depth = pos
        temp_dict['word'] = word
        temp_dict['depth'] = depth
        temp_dict['tree_position'] = pos
        temp_dict['children'] = []

        # Determine if word has parents
        if depth == 0:
            temp_dict['parent'] = 0
        # Find the parent
        else:
            for i in range(word_count):
                key = word_count - i - 1

                # Once parent is found assign parent and children
                if tree_dict[key]['depth'] == depth - 1:
                    temp_dict['parent'] = key
                    tree_dict[key]['children'].append(word_count)
                    break

        tree_dict[word_count] = temp_dict
        word_count += 1
        
        
    return tree_dict


    # self.tree_dict = tree_dict



def tree_sentiment(word_pos, tree_dict, analyzer, decay = 0.5, propagation = 10):
    '''
    Takes as input a word position (typically a named entity) and a DependencyTreeDict object.
    Output is the compiled sentiment for the word at the specified position.
    Decay controls the decay of sentiment across tree distance.
    Propagation controls how far to search through tree
    '''
    from copy import copy
    # Set key parameters
    first_sent = 0
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

    # Iterate through propagation
    # Add children before parents
    for i in range(propagation):
        phrase = ""

        # On even iterations get words by distance
        if i % 2 == 0:
            dist = int(i/2 + 1)
#             words = tree_dict.get_words_by_dist(word_pos, dist)
            words = get_words_by_dist(word_pos, tree_dict, dist)

        # On odd iterations get the same words as previous, but add children
        if i % 2 == 1:
            dist = int(i/2 + 0.5)
            words = get_words_by_dist(word_pos, tree_dict, dist)
            new_words = copy(words)
            for word in words:
                new_words += get_children(word, tree_dict, word_list = [], get_all = False)
            words = list(set(new_words))
                           
        

        for word in words:
            phrase += ' ' + str(tree_dict[word]['word'])

        # Remove the entity from phrase
        phrase = phrase.replace(str(tree_dict[word_pos]['word']), '')
        
        #print("phrase: ", phrase)

        sentiment = analyzer.polarity_scores(phrase)
        #print(sentiment)
                                             

        # Add sentiment scores into sentiment dictionary as weighted average that decreases
        # the more levels up the algorithm has compiled. Only count levels after we've established
        # some significant sentiment.

        if first_sent == 1:
            weight = (decay)**(i - first_sent_level)
            for key in compiled_sentiment.keys():
                compiled_sentiment[key] = (compiled_sentiment[key] + sentiment[key] * weight) / (1 + weight)

        if first_sent == 0 and sentiment['neu'] < 0.9:
            if sum(sentiment.values()) != 0:
                first_sent = 1
                first_sent_level = i
                compiled_sentiment = sentiment

    return compiled_sentiment


def compile_tree_sentiment(sentence, entity, nlp, analyzer, tree_dict = False, decay = 0.5, propagation = 10):
#     '''
#     Takes as input a sentence and an entity. Creates a word tree dictionary from the sentence, then finds
#     the location(s) of the entity in the word tree dictionary. For each location the function gets the
#     tree based sentiment, then compiles sentiment for each location.
#     '''
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
    # print(sentence)
    sentence = sentence.lower().replace(',', '')
    #print(tree_dict)
    if tree_dict == False:
#         tree_dict = DependencyTreeDict(sentence)
        tree_dict = get_tree_dict(sentence,nlp)
    else:
        tree_dict = tree_dict

    #print(tree_dict)
    # Find where the entity occurs in the tree dictionary
    entity_locs = []
    for key in tree_dict.keys():
        if str(tree_dict[key]['word']) == entity.lower():
            entity_locs.append(key)

    # Number of times the entity appears
    n_locs = len(entity_locs)

    # Only execute rest of function if entity is actually in sentence
    if n_locs != 0:

        # For each instance of the entity get tree sentiment
        # Add to compiled sentiment
        for loc in entity_locs:
            sentiment = tree_sentiment(loc, tree_dict, analyzer)
            for key in compiled_sentiment.keys():
                compiled_sentiment[key] += sentiment[key]

        # Divide by n_locs to get average
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] = compiled_sentiment[key] / n_locs

    return compiled_sentiment, tree_dict





def compile_split_sentiment(sentence, entity, analyzer):
    '''
    Split the sentence by comparison words and commas. Determine which sections the entity is in.
    Return average sentiment for those sections.
    '''
    # List of comparison words
    comp_words = ['but', 'however', 'albeit', 'although', 'in contrast', 'in spite of', 'though', 'on one hand', 'on the other hand',
                  'then again', 'even so', 'unlike', 'while', 'conversely', 'nevertheless', 'nonetheless', 'notwithstanding', 'yet']

    # Lowercase sentence and split on commas
    sentence = sentence.lower()
    sentence = sentence.split(',')

    # Iterate through sections and split them based on comparison words
    splits = []
    for section in sentence:

        all_comps = []
        for word in comp_words:
            # Use find all function to find location of comparison words
            all_comps += list(find_all(section, word))

        # Sort list of comparison words indexes
        all_comps.sort()

        # Split the section and append to splits
        last_split = 0
        for comp in all_comps:
            splits.append(section[last_split:comp])
            last_split = comp
        splits.append(section[last_split:])

    # Find the sections where the entity has been named
    # Add sentiment for that section to list
    sentiments = []
    for section in splits:
        if entity.lower() in section:
            # remove entity from section
            cleaned_section = section.replace(entity.lower(), '')
            sentiments.append(analyzer.polarity_scores(cleaned_section))

    # Add sentiment for each section up
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
    for sentiment in sentiments:
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] += sentiment[key]

    # Divide all sections by lenth of sentiments list to get average
    denom = len(sentiments)
    if denom != 0:
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] = compiled_sentiment[key] / denom

    return compiled_sentiment


def compile_neighborhood_sentiment(sentence, entity, analyzer, decay = 0.5, propagation = 10):
    '''
    Find instances of entity in sentence. Add sentiment of neighboring words. Incrementally expand neighborhood
    up to limit set by propagation variable. Add up sentiment with decay as neighborhood expands.
    '''
    first_sent = 0
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

    sentence = sentence.lower().replace(',', '').split(' ')

    sen_len = len(sentence)
    ent_locs = []

    # Find locations of entity within sentence
    for i, word in enumerate(sentence):
        if word == entity.lower():
            ent_locs.append(i)

    # how many entity locations there are
    n_locs = len(ent_locs)

    # Only execute rest of function if word is actually in sentence
    if n_locs != 0:

        # Iterate through propagation parameter
        for i in range(propagation):
            neighborhoods = []

            # Compile list of entity neighborhoods
            for loc in ent_locs:
                exp_locs = list(range(loc-i-1,loc+i+2))
                neigh = []
                # Only add locations to neighborhoods that are actually in the sentence
                for j in exp_locs:
                    if j >= 0 and j < sen_len:
                        neigh.append(sentence[j])
                # Join all words in neighborhood then add to neighborhoods list
                neigh = ' '.join(neigh)
                # Remove entity
                neigh = neigh.replace(entity.lower(), '')

                neighborhoods.append(neigh)

            # Get average sentiment for all neighborhoods
            sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

            for neigh in neighborhoods:
                neigh_sent = analyzer.polarity_scores(neigh)
                # Add up sentiments
                for key in sentiment.keys():
                    sentiment[key] += neigh_sent[key]

            # Divide by n_locs to get average
            for key in sentiment.keys():
                sentiment[key] = sentiment[key] / n_locs

            # Compile into main sentiment
            if first_sent == 1:
                weight = (decay)**(i - first_sent_level)
                for key in compiled_sentiment.keys():
                    compiled_sentiment[key] = (compiled_sentiment[key] + sentiment[key] * weight) / (1 + weight)

            if first_sent == 0 and sentiment['neu'] < 0.9:
                if sum(sentiment.values()) != 0:
                    first_sent = 1
                    first_sent_level = i
                    compiled_sentiment = sentiment

    return compiled_sentiment



def compile_ensemble_sentiment(sentence,aspect,nlp, analyzer, tree_dict = False):
    '''
    Determines sentiment using three different methods: neighborhood, tree, and split.
    Sentiment for each method is compiled to return a final sentiment.
    '''
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}


    tree_sentiment, tree_dict = compile_tree_sentiment(sentence,aspect,nlp, analyzer, tree_dict=False)
    neighborhood_sentiment = compile_neighborhood_sentiment(sentence, aspect,analyzer)
    split_sentiment = compile_split_sentiment(sentence, aspect, analyzer)

    all_sentiments = [tree_sentiment, neighborhood_sentiment, split_sentiment]

    # Add up all sentiment
    for sent in all_sentiments:
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] += sent[key]

    # Divide by 3 to get average
    for key in compiled_sentiment.keys():
        compiled_sentiment[key] = compiled_sentiment[key] / 3

    return compiled_sentiment, tree_dict