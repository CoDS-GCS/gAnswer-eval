#!./env python
# -*- coding: utf-8 -*-
"""
evaluation.py: evaluating gAnswer online service against QALD-3 benchmark
"""
__author__ = "Mohamed Eldesouki"
__copyright__ = "Copyright 2020, CODS Lab, GINA CODY SCHOOL OF ENGINEERING AND COMPUTER SCIENCE, CONCORDIA UNIVERSITY"
__credits__ = ["Mohamed Eldesouki"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "CODS Lab"
__email__ = "mohamed@eldesouki.ca"
__status__ = "debug"
__date__ = "2020-02-04"
import json
import time
import xml.etree.ElementTree as Et
from xml.dom.minidom import parse
from client import ask_gAnswer

q_dom = parse(r'data/dbpedia-test-questions.xml')  # parse an XML file by name


def handle_question(question):
    # question_en = question.getElementsByTagName('string')
    for q in question.getElementsByTagName('string'):
        # if element.getAttribute('A') == "1":
        if q.getAttribute('lang') == "en":
            # print([n for n in q.childNodes if n.nodeType == q.CDATA_SECTION_NODE][0])
            the_question = q.firstChild.data
            answer = ask_gAnswer(the_question, n_max_answer=1000, n_max_sparql=1000)
            return answer
            # print(q.firstChild.data, type(q.firstChild.data))


def handle_dbpedia_questions(dbpedia_questions):
    questions = dbpedia_questions.getElementsByTagName("question")
    root_element = Et.Element('dataset')
    root_element.set('id', 'dbpedia-test')

    author_comment = Et.Comment(f'created by mohamed@eldesouki.ca')
    root_element.append(author_comment)
    # with open('gAnswer_result_4', encoding='utf-8', mode='w') as rfobj:
    for i, question in enumerate(questions):
        answer = json.loads(handle_question(question))
        answer['id'] = question.attributes["id"].value
        answer['answertype'] = question.attributes['answertype'].value

        # response_json = json.loads(line.strip())
        question_element = Et.SubElement(root_element, 'question', id=question.attributes["id"].value)
        # question_element.set('id', response_json['id'])
        Et.SubElement(question_element, 'string', lang="en").text = f'![CDATA[{answer["question"]}]]'
        answers = Et.SubElement(question_element, 'answers')
        results = answer.get('results', None)
        if not results:
            continue
        # bindings = results.get('bindings', None)
        for answer in results['bindings']:
            for k, v in answer.items():
                answer_element = Et.SubElement(answers, 'answer')
                if question.attributes['answertype'].value == 'resource':
                    Et.SubElement(answer_element, 'uri').text = f'http://dbpedia.org/resource/{v["value"][1:-1]}'
                elif question.attributes['answertype'].value == 'number':
                    Et.SubElement(answer_element, 'number').text = v["value"][1:-1]
                elif question.attributes['answertype'].value == 'date':
                    Et.SubElement(answer_element, 'date').text = v["value"][1:-1]
                elif question.attributes['answertype'].value == 'boolean':
                    Et.SubElement(answer_element, 'boolean').text = v["value"][1:-1]  # True|False
                elif question.attributes['answertype'].value == 'string':
                    Et.SubElement(answer_element, 'string').text = v["value"][1:-1]
        # json.dump(answer, rfobj)
        # rfobj.write('\n')
        time.sleep(10)
        # if i == 1:
        #     break
    else:
        tree = Et.ElementTree(root_element)
        tree.write("gAnswer_03.xml")


if __name__ == '__main__':
    with parse(r'data/dbpedia-test-questions.xml') as dom:
        handle_dbpedia_questions(dom)
