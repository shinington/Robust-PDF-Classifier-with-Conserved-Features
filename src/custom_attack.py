import os
import sys


# arguments with input and output directory
try:
	in_dir = sys.argv[1]
except:
	print("need to specify relative input directory location")
	sys.exit()

try:
	out_dir = sys.argv[2]
except:
	print("need to specify relative output directory location")
	sys.exit()


print('in_dir = ' + in_dir)
print('in_dir (absolute) = ' + os.path.abspath(in_dir))
print('out_dir = ' + out_dir)
print('out_dir (absolute) = ' + os.path.abspath(out_dir))

for root, subdirs, files in os.walk(in_dir):

	for filename in files:
		file_path = os.path.join(os.path.abspath(in_dir), filename)
		out_file_path = os.path.join(os.path.abspath(out_dir), filename)

		print('\t- infile %s (full path: %s)' % (filename, file_path))
		print('\t- outfile %s (full path: %s)' % (filename, out_file_path))

		with open(file_path, 'rb') as inp:
			text = inp.read()

		# start of keywords
		new = '/#4a#61#76#61#53#63#72#69#70#74'.encode()
		text = text.replace('/JavaScript'.encode(), new)

		new = '/#41#63#74#69#6f#6e'.encode()
		text = text.replace('/Action'.encode(), new)

		new = '/#4a#53'.encode()
		text = text.replace('/JS'.encode(), new)

		new = '/#53 '.encode()
		text = text.replace('/S '.encode(), new)

		new = '/#54#79#70#65'.encode()
		text = text.replace('/Type'.encode(), new)

		new = '/#46#69#6c#74#65#72'.encode()
		text = text.replace('/Filter'.encode(), new)

		new = '/#4c#65#6e#67#74#68'.encode()
		text = text.replace('/Length'.encode(), new)

		with open(out_file_path, 'wb') as outp:
			outp.write(text)

'''
with open('open_action_js_tag.pdf', 'rb') as inp:
    text = inp.read()

#loc = text.find('JavaScript')


new = 'J#61vaScript'.encode()
text = text.replace('JavaScript'.encode(), new)

#new = 'J#53'.encode()
#text = text.replace('JS'.encode(), new)


with open('test.pdf', 'wb') as outp:
	outp.write(text)
'''