import re

lines = []

def form_table(file_name):
	global lines
	name = []
	value = []
	table_dict = {}

	counter = 0

	for line in file_name:
		lines.append(line)

	# print(lines)

	for line in lines:
		if line[0] != "\t":
			blank_index = line.find("\t")
			# print(blank_index)
			name.append(line[0:blank_index])
			num_line = [int(i) for i in line.split() if i.isdigit()]
			if num_line:
				# print(num_line)
				counter -= 2
				for num in num_line:
					value.append(num)
			else:
				value.append(counter)

		# match = re.match(r'BALR', line, re.M|re.I)
		# print(match)
		if line.find("BALR") != -1:
			counter += 2
			continue
		
		if line.find("USING") != -1:
			continue

		if line.find("BNE") != -1:
			counter += 2
			continue
		
		if line.find("BR") != -1:
			counter += 2
			continue
		
		if line.find("START") == -1:
			counter += 4

	for key in name: 
		for val in value: 
			table_dict[key] = val
			value.remove(val) 
			break

	return table_dict

def pass1(file_name, table_dict):
	global lines
	line_dup = []
	pass1 = []
	pass1_dup = []
	relative_addr = []
	pass1_output = {}
	counter = 0

	keys = [key for key in table_dict.keys()]
	# print(keys)

	for line in lines:
		line_dup.append(line)
	
	for line in line_dup:
		for key in keys:
			if line.find(key) != -1:
				if line.find("LOOP") != -1:
					continue
				if line.find(key) > 0:
					continue
				# print(line.find(key))
				line_dup.remove(line)
				break
	# print(line_dup)

	regex = re.compile(r'[\n\r\t]')

	for line in line_dup:
		line = regex.sub("", line)
		# print(line)
		if line.find("USING") != -1:
			continue
		pass1.append(line)
		# line_dup.append(line)

	# print(pass1)
	for line in pass1:
		for key in keys:
			if line.find(key) == 0:
				temp = line.replace(key, "", 1)
				for x, temp_line in enumerate(pass1):
					if pass1[x] == line:
						pass1[x] = temp
						break
	# print(pass1)
	for line in pass1:
		pass1_dup.append(line)

	for line in pass1:
		for key in keys:
			if line.find(key) > 0:
				temp = line.replace(key, "_")
				for x, temp_line in enumerate(pass1):
					if pass1[x] == line:
						pass1[x] = temp
						break
	# print(pass1)
	for line in pass1:
		for key in keys:
			if line.find(key) > 0:
				temp = line.replace(key, "_")
				for x, temp_line in enumerate(pass1):
					if pass1[x] == line:
						pass1[x] = temp
						break
	# print(pass1)
	for line in pass1:
		relative_addr.append(counter)
		if line[-1] == "_":
			temp = line + "(0, 15)"
			for x, temp_line in enumerate(pass1):
				if pass1[x] == line:
					pass1[x] = temp
					break
			counter += 4
			continue
		elif line.find("DC") != -1:
			temp = line[-1]
			for x, temp_line in enumerate(pass1):
				if pass1[x] == line:
					pass1[x] = temp
					break
			counter += 4
			continue
		elif line.find("END") != -1:
			temp = " "
			for x, temp_line in enumerate(pass1):
				if pass1[x] == line:
					pass1[x] = temp
					break
			counter += 4
			continue
		elif line.find("BR") != -1:
			temp = line.replace(" ", " 15, ", 1)
			for x, temp_line in enumerate(pass1):
				if pass1[x] == line:
					pass1[x] = temp
					break
			counter += 2
			continue
		elif line.find("CLI") != -1:
			counter += 4
			continue
		counter += 2		
	# print(pass1)
	# print(relative_addr)
	for key in relative_addr: 
		for val in pass1: 
			pass1_output[key] = val
			pass1.remove(val) 
			break

	return pass1_output, pass1_dup

def pass2(pass1_ref, pass1_output, table_dict):
	pass1_list = []
	pass2_inst = []
	relative_addr = []
	pass2_output = {}

	for key in pass1_output.keys():
		pass1_list.append(pass1_output[key])
		relative_addr.append(key)

	# print(relative_addr)

	length = len(pass1_list) - 1
	# print(length)
	# print(pass1_ref)
	# print(pass1_list)

	while length >= 0:
		if pass1_list[length] == pass1_ref[length]:
			# print("euqal "+pass1_list[length])
			pass2_inst.append(pass1_list[length])
		else:
			# print("not equal "+pass1_list[length])
			first_reg_index = pass1_list[length].find("_")
			if first_reg_index > 0:
				sub_inst = pass1_ref[length][first_reg_index:len(pass1_ref)]
				if sub_inst.find(",") != -1:
					comma_index = sub_inst.find(",")
					first_reg = sub_inst[:comma_index]
					for key in table_dict.keys():
						if first_reg == key:
							first_reg_val = table_dict[key]
							break
					pass2_sub_inst = pass1_list[length].replace("_", str(first_reg_val), 1)
					pass2_inst.append(pass2_sub_inst)
				else:
					# print(sub_inst)
					if sub_inst.find("+") != -1 or sub_inst.find("-") != -1 or sub_inst.find("/") != -1 or sub_inst.find("*") != -1:
						first_reg = sub_inst[:-1]
					else:
						first_reg = sub_inst[:]
					for key in table_dict.keys():
						if first_reg == key:
							first_reg_val = table_dict[key]
							break
					pass2_sub_inst = pass1_list[length].replace("_", str(first_reg_val), 1)
					pass2_inst.append(pass2_sub_inst)
			elif first_reg_index < 0:
				pass2_inst.append(pass1_list[length])
		length -= 1

	pass2_inst.reverse()
	# print(pass2_inst)
	length = len(pass2_inst) -1

	while length >= 0:
		if pass2_inst[length].find("_") != -1:
			# print(pass1_ref[length])
			index = pass1_ref[length].find(",")
			second_reg = pass1_ref[length][index+2:]
			# print(second_reg)
			for key in table_dict.keys():
				if second_reg == key:
					second_reg_val = table_dict[key]
					break
			pass2_sub_inst = pass2_inst[length].replace("_", str(second_reg_val), 1)
			pass2_inst[length] = pass2_sub_inst
		length -= 1

	# print(pass1_list)
	
	# print(pass2_inst)
	for key in relative_addr: 
		for val in pass2_inst: 
			pass2_output[key] = val
			pass2_inst.remove(val) 
			break

	return pass2_output

macro = open("macro.txt")

table_dict = form_table(macro)

print("Input Macro is: \n")
for line in lines:
	print(line)

print("\n\nTable is: \n")
print("NAME\t|\tVALUE")
print("--------|---------")
for key in table_dict.keys():
	if len(key) <= 3:
		print(key+"\t\t|\t",table_dict[key])
	else:
		print(key+"\t|\t",table_dict[key])
print("--------|---------")

pass1_output, pass1_ref = pass1(macro, table_dict)
print("\nPass1 Output: \n")
print("RelativeAddr|\tInstruction")
print("------------|-----------------")
for key in pass1_output.keys():
	print(key,"\t\t\t|\t",pass1_output[key])
print("------------|-----------------")

pass2_output = pass2(pass1_ref, pass1_output, table_dict)
print("\nPass2 Output: \n")
print("RelativeAddr|\tInstruction")
print("------------|-----------------")
for key in pass2_output.keys():
	print(key,"\t\t\t|\t",pass2_output[key])
print("------------|-----------------")




