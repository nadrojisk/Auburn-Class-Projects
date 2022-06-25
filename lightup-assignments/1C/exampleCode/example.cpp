/*
This is a sample program to illustrate argument passing in C++ and enable the
run.sh script to compile and run a program.
*/
#include <iostream>

using namespace std;

int main(int argc, char* argv[])
{
	if(argc == 3)
	{
		cout << "The problem file passed is: " << argv[1] << endl;
		cout << "The config file passed is: " << argv[2] << endl;
	}else if(argc == 2)
	{
		cout << "The problem file passed is: " << argv[1] << endl;
		cout << "Using the default config file since none was specified!" << endl;
	}
	else
	{
		cout << "An inappropriate number of arguments were passed!" << endl;
	}

	return 0;
}