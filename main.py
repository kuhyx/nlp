import processing
import pandas as pd

# paths to students andsewrs database
studentAnswers1_path = "test_goldStandard/student/STSint.testinput.answers-students.sent1.txt"
studentAnswers2_path = "test_goldStandard/student/STSint.testinput.answers-students.sent2.txt"
studentAnsewrs_chunked_path1 = "test_goldStandard/student/STSint.testinput.answers-students.sent1.chunk.txt"
studentAnsewrs_chunked_path2 = "test_goldStandard/student/STSint.testinput.answers-students.sent2.chunk.txt"
studentsAnsewrs_alignment_path = "test_goldStandard/student/STSint.testinput.answers-students.wa"

# load data
studentAnserws = processing.load_sentences(studentAnswers1_path, studentAnswers1_path)
goldstandard_chunked = processing.load_chunked(studentAnsewrs_chunked_path1, studentAnsewrs_chunked_path2)
goldstandard_alignment = processing.load_alignment(studentsAnsewrs_alignment_path)

# get a nice anwser-student table
data = pd.merge(goldstandard_chunked, goldstandard_alignment, left_index=True, right_index=True)
print(data)

# generate a few examples
for i in range(1, 10):
    print(processing.generate_alignment_format(data, i))
    print("correct anwser for this is: ")
    print(data["alignment_text"][i])

# best prompt so far
prompt = """
Given the input (pairs of sentences divided into chunks) align the corresponding chunks. The chunks are based on those used in the CoNLL 2000 chunking task (Abney 1991, Tjong et al. 2000), with some adaptations.

the steps required fot this are as follows:

A. When aligning, take into account the deep meaning of the chunk in context, beyond the surface.
B. One chunk can be aligned to more than one chunk, but only to prevent unaligned chunks.
C. Do all 1:1 alignments first. When having two options to align, choose the strongest corresponding one first. A 1:1 alignment is comparing each chunk from one sentance to each chunk from the other sentance. 
D. After doing 1:1 alignments, check unaligned chunks. There are three options to align them, in this order of preference:
	1. Insert the unaligned chunk (or group of chunks) into an existing 1:1 alignment.
	2. Create a new relation, add a new score and label to the new relation.
	3. Chunks can be left unaligned if no corresponding chunk can be found. They are then assigned a NOALI label with score 0 with a relation to a non existing chunk 0
E. Assign at least one label to each alignment.
F. Try to leave as few unaligned chunks as possible.
G. Keep it simple
H. You can leave punctuations unaligned, as they will be ignored when evaluating. The interface requires that you annotate all tokens, so please tag them with the label for unaligned chunks

The scores are defined as follows:
A similarity/relatedness score between the aligned chunks, from 5 (maximum similarity/relatedness) to 0 (no relation at all):
    5 if the meaning of both chunks is equivalent
    [4,3] iff the meaning of both chunks is very similar or closely related
    [2,1] iff the meaning of both chunks is slightly similar or somehow related
    0 iff the meaning of both chunks is completely unrelated.

What is more, there are different possible types of alignment:
	EQUI: both chunks have the same meaning, they are semantically equivalent in this context.
	OPPO: the meanings of the chunks are in opposition to each other, lying in an inherently incompatible binary relationship.
	SPE1: both chunks have similar meanings, but chunk in sentence 1 is more specific.
	SPE2: like SPE1, but it is the chunk in sentence 2 which is more specific.
	SIMI: both chunks have similar meanings, they share similar attributes and there is no EQUI, OPPO, SPE1 or SPE2 relation
	REL: both chunks are not considered similar but they are closely related by some relation not mentioned above (i.e. no EQUI, OPPO, SPE1, SPE2, or SIMI relation).
	NOALI: this chunk has not any corresponding chunk in the other sentence. Therefore, it is left unaligned.

Scores for NOALI will be ignored. EQUI should have a 5 score. The rest should have a score bigger than 0 but lower than 5.

the data will be provided in this format:
seq1:
1) sequance 1 chunk 1
2) sequance 1 chunk 2
3) sequance 1 chunk 3
...

seq2:
1) sequance 2 chunk 1
2) sequance 2 chunk 2
3) sequance 2 chunk 3
...

where seq1: and seq2: indicate the beggining of a new chunk sequance. Each chunk beggins with a number that indicates the tokend-id. 


Each alignment is reported in one line as follows:
  token-id-seq1 <==> token-id-seq2 // type // score // comment

where:
	token-id-seq1 is a sequence of token indices (starting at 1) for the chunk(s) in sentence 1 (or 0 if the chunk in sentence 2 is not aligned)
	token-id-seq2 is a sequence of token indices (starting at 1) for the chunk(s) in sentence 2 (or 0 if the chunk in sentence 1 is not aligned)
	type is composed of one of the obligatory labels, concatenated to the optional ones by '_'
	score is a number from 0 to 5, or NIL (if type label is NOALI)
	comment is chunks written in their text form and an explanation of the relation 

using the terminology form input data example, if a chunk has a single relation for example sequance 1 chunk 1 with sequance 2 chunk 1 report it as:
1 <==> 1 // type // score // comment

if there are multiple chunks in relation with each other, seperate them with spaces. For example:
1 <==> 1 2 // type // score // comment
or 
2 3 <==> 1 2 // type // score / comment 

provide the answer for final chunk relations as a plain text list of relations. 
"""