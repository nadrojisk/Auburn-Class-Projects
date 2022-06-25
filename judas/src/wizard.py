payloads = ["Message Box Popup", "TCP Reverse Shell"]
payload_choices = ['msg', 'rev']


def run(args):
    print("What type of payload would you like to inject?")
    for count, payload in enumerate(payloads):
        print(f'{count}: {payload}')
    choice = payload_choices[int(input())]
    args.type = choice
    if choice == 'msg':
        # msg box
        pass
    elif choice == 'rev':
        # tcp reverse
        args.lhost = input("What IP would you like to listen on: ")
        args.lport = input("What port would you like to listen on: ")
    return args
