# -*- coding: utf-8 -*-

"""
***********************************************************************************************************************
***********************************************************************************************************************
***********************************************************************************************************************

C O D I G O   C O P I A D O   D E   D E E P - B G T (BEGIN)

***********************************************************************************************************************
***********************************************************************************************************************
***********************************************************************************************************************
"""
import copy as cp
import re
import io
import pandas as pd
import codecs


def tag_bigappy_unicrossy(path):
    
    train_corpus = read_corpus(path)
    train_tagged_path = path.replace(".cupt", "_tagged.cupt")

    train_corpus['BIO'] = cp.deepcopy(train_corpus['PARSEME:MWE'])
    train_corpus[train_corpus['BIO'].isnull()] = 'space'

    # remove other tags after the first tag
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d:\\w+[.]*\\w+;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(lambda x: x.strip())

    sentence_indexes = [-1] + list(train_corpus.loc[train_corpus['BIO'] == 'space'].index)

    # tag sentence by sentence
    for i, sentence_idx in enumerate(sentence_indexes[:-1]):
        sentence = train_corpus[sentence_idx + 1:sentence_indexes[i + 1]]
        o_indexes = []
        last_B_idx = 0
        last_b_idx = 0
        isB = False
        # j -> each token in the sentence
        # only 1 B(I) and 1 b(i) is taken into consideration simultaneously
        # allows crossings
        for j, row in sentence.iterrows():
            tag = sentence.loc[j, 'BIO']
            # if (there is a tag in the form of no:category and it is the first VMWE in the sentence)
            # or (there is a tag in the form of no:category
            # and it is the beginning of an VMWE after the last B(I) tagged VMWE ends)
            # it does not wait the end of the nested VMWE to begin a new B(I) tagged VMWE
            # B I b i I I B i I is possible
            # only 1 B is allowed - 1 level
            if (bool(re.match("\\d:", tag)) and not isB) or (bool(re.match("\\d:", tag)) and j > last_B_idx):
                isB = True
                no = tag.split(':')[0]
                category = tag.split(':')[1]
                category = category.strip()
                train_corpus.loc[j, 'BIO'] = 'B:' + category
                # stores I indexes
                I_indexes = list(sentence.loc[train_corpus['BIO'] == no].index)
                # if it is multi-token VMWE
                if len(I_indexes) > 0:
                    for k in I_indexes:
                        train_corpus.loc[k, 'BIO'] = 'I:' + category
                    last_B_idx = I_indexes[-1]
                    # it is multi-token VMWE, so there is a possibility of gap
                    # add the beginning index and the end index of the VMWE
                    o_indexes.append([j, last_B_idx])
                # if it is single-token VMWE
                else:
                    last_B_idx = j

            # if (there is a tag in the form of no:category and
            # it is a nested VMWE since its in between the last BI tagged VMWE)
            # and it is the first nested VMWE in between the last BI tagged VMWE
            # only 1 b is allowed - 1 level
            # since the location of i is not checked, it allows crossing
            elif (bool(re.match("\\d:", tag)) and j < last_B_idx) and j > last_b_idx:
                no = tag.split(':')[0]
                category = tag.split(':')[1]
                category = category.strip()
                train_corpus.loc[j, 'BIO'] = 'b:' + category
                # stores i indexes
                i_indexes = list(sentence.loc[train_corpus['BIO'] == no].index)
                # if it is multi-token VMWE
                if len(i_indexes) > 0:
                    for l in i_indexes:
                        train_corpus.loc[l, 'BIO'] = 'i:' + category
                    last_b_idx = i_indexes[-1]
                    # it is multi-token VMWE, so there is a possibility of gap
                    # add the beginning index and the end index of the VMWE
                    o_indexes.append([j, last_b_idx])
                # if it is single-token VMWE
                else:
                    last_b_idx = j

        for o_idx in o_indexes:
            for oo_idx in range(o_idx[0] + 1, o_idx[1]):
                tag = sentence.loc[oo_idx, 'BIO']
                # if there is no tag in between an multi-token MWE, tag with 'o'
                if not (bool(re.match("I:", tag)) or bool(re.match("B:", tag)) or bool(re.match("i:", tag)) or bool(
                        re.match("b:", tag))):
                    train_corpus.loc[oo_idx, 'BIO'] = 'o'

    # tags with 'O'
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: 'O' if not (bool(re.match("i:", x)) or bool(re.match("b:", x)) or bool(re.match("I:", x)) or bool(
            re.match("B:", x)) or bool(re.match("o", x)) or bool(re.match("space", x))) else x)

    # self._train_corpus.to_csv(fileName)
    to_cupt(train_corpus, train_tagged_path)


def tag_gappy_1_level(path):
    
    train_corpus = read_corpus(path)
    train_tagged_path = path.replace(".cupt", "_tagged.cupt")

    train_corpus['BIO'] = cp.deepcopy(train_corpus['PARSEME:MWE'])
    train_corpus[train_corpus['BIO'].isnull()] = 'space'

    # remove other tags after the first tag
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d:\\w+[.]*\\w+;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(lambda x: x.strip())

    sentence_indexes = [-1] + list(train_corpus.loc[train_corpus['BIO'] == 'space'].index)

    # tag sentence by sentence
    for i, sentence_idx in enumerate(sentence_indexes[:-1]):
        sentence = train_corpus[sentence_idx + 1:sentence_indexes[i + 1]]
        o_indexes = []
        last_B_idx = 0
        last_b_idx = 0
        isB = False
        # j -> each token in the sentence
        # only 1 B(I) and 1 b(i) is taken into consideration simultaneously
        # does not allow crossings
        for j, row in sentence.iterrows():
            tag = sentence.loc[j, 'BIO']
            # if (there is a tag in the form of no:category and it is the first VMWE in the sentence)
            # or (there is a tag in the form of no:category
            # and it is the beginning of an VMWE after the last B(I) tagged VMWE ends)
            # only 1 B is allowed - 1 level
            if (bool(re.match("\\d:", tag)) and not isB) or (bool(re.match("\\d:", tag)) and j > last_B_idx):
                isB = True
                no = tag.split(':')[0]
                category = tag.split(':')[1]
                category = category.strip()
                train_corpus.loc[j, 'BIO'] = 'B:' + category
                # stores I indexes
                I_indexes = list(sentence.loc[train_corpus['BIO'] == no].index)
                # if it is multi-token VMWE
                if len(I_indexes) > 0:
                    for k in I_indexes:
                        train_corpus.loc[k, 'BIO'] = 'I:' + category
                    last_B_idx = I_indexes[-1]
                    # it is multi-token VMWE, so there is a possibility of gap
                    # add the beginning index and the end index of the VMWE
                    o_indexes.append([j, last_B_idx])
                # if it is single-token VMWE
                else:
                    last_B_idx = j

            # if (there is a tag in the form of no:category and
            # it is a nested VMWE since its in between the last BI tagged VMWE)
            # and it is the first nested VMWE in between the last BI tagged VMWE
            # only 1 b is allowed - 1 level
            # since the location of i is checked, it does not allow crossing
            elif (bool(re.match("\\d:", tag)) and j < last_B_idx) and j > last_b_idx:
                prev_last_b_idx = last_b_idx
                no = tag.split(':')[0]
                category = tag.split(':')[1]
                category = category.strip()
                # stores i indexes
                i_indexes = list(sentence.loc[train_corpus['BIO'] == no].index)
                # if it is multi-token VMWE
                if len(i_indexes) > 0:
                    valid_b = 0
                    last_b_idx = i_indexes[-1]
                    if last_b_idx < last_B_idx:
                        valid_b = 1
                        if not i_indexes[0] - j == 1:
                            valid_b = 0
                        for i_idx in range(1, len(i_indexes)):
                            if not i_indexes[i_idx] - i_indexes[i_idx - 1] == 1:
                                valid_b = 0
                        if valid_b == 1:
                            for n_idx in range(j + 1, last_b_idx):
                                tagg = sentence.loc[n_idx, 'BIO']
                                # if there is no tag in between an nested MWE, tag with nested MWE
                                # if there is a tag, invalid nested MWE
                                if bool(re.match("I:", tagg)) or bool(re.match("B:", tagg)) or bool(
                                        re.match("i:", tagg)) or bool(re.match("b:", tagg)):
                                    valid_b = 0
                    if valid_b == 1:
                        train_corpus.loc[j, 'BIO'] = 'b:' + category
                        for l in i_indexes:
                            train_corpus.loc[l, 'BIO'] = 'i:' + category
                    if valid_b == 0:
                        last_b_idx = prev_last_b_idx
                # if it is single-token VMWE
                else:
                    train_corpus.loc[j, 'BIO'] = 'b:' + category
                    last_b_idx = j

        for o_idx in o_indexes:
            for oo_idx in range(o_idx[0] + 1, o_idx[1]):
                tag = sentence.loc[oo_idx, 'BIO']
                # if there is no tag in between an multi-token MWE, tag with 'o'
                if not (bool(re.match("I:", tag)) or bool(re.match("B:", tag)) or bool(re.match("i:", tag)) or bool(
                        re.match("b:", tag))):
                    train_corpus.loc[oo_idx, 'BIO'] = 'o'

    # tags with 'O'
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: 'O' if not (bool(re.match("i:", x)) or bool(re.match("b:", x)) or bool(re.match("I:", x)) or bool(
            re.match("B:", x)) or bool(re.match("o", x)) or bool(re.match("space", x))) else x)

    # self._train_corpus.to_csv(fileName)
    to_cupt(train_corpus, train_tagged_path)

def tag_IOB(path):
    
    train_corpus = read_corpus(path)
    train_tagged_path = path.replace(".cupt", "_tagged.cupt")
    
    train_corpus['BIO'] = cp.deepcopy(train_corpus['PARSEME:MWE'])
    train_corpus[train_corpus['BIO'].isnull()] = 'space'

    # remove other tags after the first tag
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d:\\w+[.]*\\w+;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: x.split(';')[0] if bool(re.match("\\d;.", x)) else x)
    train_corpus['BIO'] = train_corpus['BIO'].apply(lambda x: x.strip())

    sentence_indexes = [-1] + list(train_corpus.loc[train_corpus['BIO'] == 'space'].index)

    # tag sentence by sentence
    for i, sentence_idx in enumerate(sentence_indexes[:-1]):
        sentence = train_corpus[sentence_idx + 1:sentence_indexes[i + 1]]
        last_B_idx = 0
        isB = False
        for j, row in sentence.iterrows():
            tag = sentence.loc[j, 'BIO']
            if (bool(re.match("\\d:", tag)) and not isB) or (bool(re.match("\\d:", tag)) and j > last_B_idx):
                isB = True
                no = tag.split(':')[0]
                category = tag.split(':')[1]
                category = category.strip()
                train_corpus.loc[j, 'BIO'] = 'B:' + category
                I_indexes = list(sentence.loc[train_corpus['BIO'] == no].index)
                if len(I_indexes) > 0:
                    for k in I_indexes:
                        train_corpus.loc[k, 'BIO'] = 'I:' + category
                    last_B_idx = I_indexes[-1]
                else:
                    last_B_idx = j

    train_corpus['BIO'] = train_corpus['BIO'].apply(
        lambda x: 'O' if not (
                bool(re.match("I:", x)) or bool(re.match("B:", x)) or bool(re.match("space", x))) else x)

    # self._train_corpus.to_csv(fileName)
    to_cupt(train_corpus, train_tagged_path)

def read_corpus(path):
    corpus_file = io.open(path, "r", encoding="utf-8")
    corpus = []
    for s in corpus_file:
        if not s.startswith('#'):
            corpus.append(s)
    corpus = [x.split('\t') for x in corpus]
    new_corpus = pd.DataFrame(corpus,
                              columns=['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL',
                                       'DEPS', 'MISC',
                                       'PARSEME:MWE'])
    return new_corpus

def to_cupt(df, cupt_path):
    print('Writing to %s...' % cupt_path)
    lines = ''
    for idx, row in df.iterrows():
        if row['PARSEME:MWE'] == 'space':
            line = '\n'
        else:
            line = str(row['ID']) + '\t' + row['FORM'] + '\t' + row['LEMMA'] + '\t' + row['UPOS'] + '\t' + row[
                'XPOS'] + '\t' + row['FEATS'] + '\t' + row['HEAD'] + '\t' + row['DEPREL'] + '\t' + row[
                       'DEPS'] + '\t' + row['MISC'] + '\t' + row['BIO'] + '\n'
        lines += line

    f = codecs.open(cupt_path, "w", "utf-8")
    f.write(lines)
    f.close()


"""
***********************************************************************************************************************
***********************************************************************************************************************
***********************************************************************************************************************

C O D I G O   C O P I A D O   D E   D E E P - B G T (END)

***********************************************************************************************************************
***********************************************************************************************************************
***********************************************************************************************************************
"""