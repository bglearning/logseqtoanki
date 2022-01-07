import csv 
import os
import sys


def find_occurrences(sub_str, s):
    i = s.find(sub_str)
    while i != -1:
        yield i
        i = s.find(sub_str, i + 1)


def handle_latex(s):
    # Remove escape character on '\' i.e. replace "\\" with "\"
    s = s.replace("\\\\", "\\")

    delim_occurrences = list(find_occurrences("$$", s))
    assert len(delim_occurrences) % 2 == 0, s

    for i, delim_index in enumerate(delim_occurrences):
        if i % 2 == 0:
            s = s[:delim_index] + "\[" + s [delim_index + 2 : ]
        else:
            s = s[:delim_index] + "\]" + s [delim_index + 2 : ]

    delim_occurrences = list(find_occurrences("$", s))
    assert len(delim_occurrences) % 2 == 0, s

    # We need this offset as adding the two-character delim as a replacement
    # of the one character "$" screws up the delim_occurrences index by 1
    offset = 0
    for i, delim_index in enumerate(delim_occurrences):
        delim_index = delim_index + offset
        if i % 2 == 0:
            s = s[:delim_index] + "\(" + s [delim_index + 1 : ]
        else:
            s = s[:delim_index] + "\)" + s [delim_index + 1 : ]

        offset += 1 

    return s


def format_line(s):
    s = s.replace("#card", "")

    # LaTeX handling -------
    s = handle_latex(s)
    return s


def main():
    if len(sys.argv) != 3:
        print('Usage: python logseq_to_anki.py path/to/page/in/logseq output_filename_base')
        sys.exit(os.EX_USAGE)

    input_file = sys.argv[1]
    output_filename_base = sys.argv[2]

    card_tab_level = 999
    inside_card = False
    card_question = ""
    card_answer = ""
    block_content = ""
    q_and_a_list = []
    q_and_a_list_cloze = []


    for line in open(input_file):
        # Logseq uses the collapsed:: tag to denote whether a block is collapsed or not
        if "collapsed::" in line:
            continue

        num_of_tabs = line.count('\t')
        untabbed_line = line.replace('\t', '')
        if untabbed_line.startswith('- '):
            block_content = untabbed_line[2:]
        else:
            block_content += untabbed_line

        if num_of_tabs <= card_tab_level:
            inside_card = False
            card_tab_level = 999
            if card_question and card_answer:
                q_and_a_list.append((format_line(card_question), format_line(card_answer)))
                card_question, card_answer = "", ""

        if inside_card:
            card_answer = block_content

        if "#card" in line:
            card_tab_level = num_of_tabs
            card_question += block_content
            if "cloze" in block_content:
                q_and_a_list_cloze.append(format_line(card_question).replace("{{cloze", "{{c1::"))
                card_question, card_answer = "", ""
            else:
                inside_card = True


    if len(q_and_a_list) > 0:
        print(f'{len(q_and_a_list)} normal questions')
        with open(f"{output_filename_base}.tsv", 'w', encoding='utf8', newline='') as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')

            for q, a in q_and_a_list:
                tsv_writer.writerow([q, a])

    if len(q_and_a_list_cloze) > 0:
        print(f'{len(q_and_a_list_cloze)} cloze questions')
        with open(f"{output_filename_base}_cloze.tsv", 'w', encoding='utf8', newline='') as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')

            for q in q_and_a_list_cloze:
                tsv_writer.writerow([q])



if __name__ == '__main__':
    main()
