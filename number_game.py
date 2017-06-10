import random

def game():
	secret_num = random.randint(1, 10)
	max_permitted_mistakes = 5

	bad_guesses = []

	while len(bad_guesses) < max_permitted_mistakes:
		try:
			guess = int(raw_input("Guess a number between 1 and 10: "))

		except ValueError:
			print("{} is not a number! ".format(guess))

		else:
			if guess == secret_num:
				print("You got it! My number was {}".format(secret_num))
				break
			elif guess < secret_num:
				print("My number is higher than {}".format(guess))
			else:
				print("My number is lower than {}".format(guess))

			bad_guesses.append(guess)

	else:
		print("You did not get it! My number was {}".format(secret_num))

	replay_input = raw_input("Do you wan to play again? Y/n ")

	if replay_input.lower() != 'n':
		game()
	else: 
		print("Bye!")

game()