# make a list to hold onto our items
shopping_list = []

# print out instructions on how to use the application
print("What should we pick up at the store?")
print("Enter 'DONE' to stop adding items.")

while True:
	# ask for new items
	new_item = raw_input("> ")

	if new_item == 'DONE':
		break

	# add new items to our list
	shopping_list.append(new_item)

print("Here's your list: ")

for item in shopping_list:
	print(item)