import random

# the list of words
words = [
	'apple',
	'banana',
	'orange',
	'coconut',
	'strawberry',
	'lime',
	'grapefruit',
	'lemon',
	'kumquat',
	'blueberry',
	'melon'
]

max_permitted_mistakes = 7

while True:
	start = raw_input("Press enter / Return to start, or Q to quit")

	if start == 'Q' or start.lower() == 'q':
		break

	secret_word = random.choice(words)
	# for storing letters that are not in the secret word
	bad_guesses = []
	# for storing letters that are not in the secret word
	good_guesses = []

	# list method converts string to array
	while len(bad_guesses) < max_permitted_mistakes and len(good_guesses) != len(list(secret_word)):
	 	for letter in secret_word:
	 		if letter in good_guesses:
	 			print letter
 			else:
 				print '_'

		print('')
		print('Strikes: {} / {}'.format(len(bad_guesses), max_permitted_mistakes))
		print('')

		# console input 
		guess = raw_input("Guess a letter: ").lower()

		if len(guess) > 1:
			print("You can only guess a single letter")
			continue
		elif guess in bad_guesses or guess in good_guesses:
			print("You have already guessed that letter!")
			continue
		# isalpha method checkes if a given string is all alphabets.
		elif not guess.isalpha():
			print("You can only guess letters!")
			continue

		# when input letter is in secret_word
		if guess in secret_word:
			good_guesses.append(guess)

			if len(good_guesses) == len(list(secret_word)):
				print("You win! The word has {}".format(secret_word))
				break

		else:
				bad_guesses.append(guess)

	else: 
		print("You didn't guess it! My word was {}".format(secret_word))


