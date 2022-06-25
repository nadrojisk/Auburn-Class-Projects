#!/usr/bin/python3

'''
This is a sample program to illustrate non-robust argument passing in Python
to enable the run.sh script to call a Python program
'''

from sys import argv

def main():
	if len(argv) == 3:
		print(f'The problem file passed is: {argv[1]}')
		print(f'The config file passed is: {argv[2]}')
	elif len(argv) == 2:
		print(f'The problem file passed is: {argv[1]}')
		print('Using the default config file since none was specified!')
	else:
		print('An inappropriate number of arguments were passed!')

if __name__ == '__main__':
	main()